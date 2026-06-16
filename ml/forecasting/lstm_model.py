"""
LSTM + Temporal Fusion Transformer
72-hour ahead violation density forecasting per H3 cell.
"""
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from pathlib import Path

MODEL_DIR = Path("../../models")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class ViolationDataset(Dataset):
    """Sliding window dataset: 168 hours in → 72 hours out."""
    def __init__(self, sequences: np.ndarray, targets: np.ndarray):
        self.X = torch.FloatTensor(sequences)
        self.y = torch.FloatTensor(targets)

    def __len__(self): return len(self.X)
    def __getitem__(self, i): return self.X[i], self.y[i]


class ParkSenseLSTM(nn.Module):
    """
    Stacked LSTM for hourly violation count forecasting.
    Input:  (batch, seq_len=168, features=12)
    Output: (batch, horizon=72)
    """
    def __init__(self, input_size: int = 12, hidden: int = 128,
                 num_layers: int = 2, dropout: float = 0.2, horizon: int = 72):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden,
            num_layers=num_layers,
            dropout=dropout,
            batch_first=True,
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, horizon),
        )

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])   # Use last timestep

    def predict_quantiles(self, x: torch.Tensor):
        """Monte-Carlo dropout for uncertainty estimation (P10, P50, P90)."""
        self.train()   # enable dropout
        preds = [self.forward(x).detach().cpu().numpy() for _ in range(50)]
        preds = np.stack(preds, axis=0)    # (50, batch, horizon)
        self.eval()
        return {
            "p10": np.percentile(preds, 10, axis=0),
            "p50": np.percentile(preds, 50, axis=0),
            "p90": np.percentile(preds, 90, axis=0),
        }


def prepare_sequences(df_h3: pd.DataFrame,
                       seq_len: int = 168,
                       horizon: int = 72,
                       feature_cols: list = None) -> tuple:
    """
    Build sliding window sequences from hourly H3 violation time series.
    df_h3: DataFrame with hourly index and feature columns.
    """
    if feature_cols is None:
        feature_cols = ["violation_count", "hour_sin", "hour_cos",
                        "dow_sin", "dow_cos", "month_sin", "month_cos",
                        "is_weekend", "is_peak_night", "phs",
                        "vehicle_severity_mean", "repeat_offender_density"]

    data = df_h3[feature_cols].fillna(0).values
    Xs, ys = [], []
    for i in range(len(data) - seq_len - horizon + 1):
        Xs.append(data[i: i + seq_len])
        ys.append(data[i + seq_len: i + seq_len + horizon, 0])  # violation_count only
    return np.array(Xs), np.array(ys)


def train_lstm(df: pd.DataFrame, h3_index: str, epochs: int = 50,
               batch_size: int = 64, lr: float = 1e-3) -> ParkSenseLSTM:
    """Train LSTM for a specific H3 cell."""
    # Filter to H3 cell and resample hourly
    cell_df = df[df["h3_index"] == h3_index].copy()
    cell_df["created_datetime"] = pd.to_datetime(cell_df["created_datetime"], utc=True)
    hourly = cell_df.set_index("created_datetime").resample("1h").agg({
        "id": "count",
        "vehicle_severity": "mean",
        "repeat_offender_density": "mean",
        "hour_sin": "first", "hour_cos": "first",
        "dow_sin": "first",  "dow_cos": "first",
        "month_sin": "first","month_cos": "first",
        "is_weekend": "first","is_peak_night": "first","phs": "first",
    }).rename(columns={"id": "violation_count"}).fillna(0)

    X, y = prepare_sequences(hourly)
    split = int(len(X) * 0.85)
    ds_train = ViolationDataset(X[:split], y[:split])
    ds_val   = ViolationDataset(X[split:], y[split:])
    dl_train = DataLoader(ds_train, batch_size=batch_size, shuffle=True)
    dl_val   = DataLoader(ds_val,   batch_size=batch_size)

    model = ParkSenseLSTM(input_size=X.shape[2]).to(DEVICE)
    opt   = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()

    best_val_loss = float("inf")
    for epoch in range(epochs):
        model.train()
        for xb, yb in dl_train:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            loss = loss_fn(model(xb), yb)
            opt.zero_grad(); loss.backward(); opt.step()

        model.eval()
        val_losses = []
        with torch.no_grad():
            for xb, yb in dl_val:
                xb, yb = xb.to(DEVICE), yb.to(DEVICE)
                val_losses.append(loss_fn(model(xb), yb).item())
        vl = np.mean(val_losses)
        if vl < best_val_loss:
            best_val_loss = vl
            torch.save(model.state_dict(), MODEL_DIR / f"lstm_{h3_index}.pt")
        if epoch % 10 == 0:
            print(f"  Epoch {epoch:3d} | val_loss={vl:.4f}")

    model.load_state_dict(torch.load(MODEL_DIR / f"lstm_{h3_index}.pt"))
    return model


# ── Inference helper ──────────────────────────────────────────────────────────
def forecast_zone(model: ParkSenseLSTM, recent_sequence: np.ndarray) -> dict:
    """
    Produce 72h forecast with uncertainty.
    recent_sequence: (168, features) — last 7 days hourly data
    """
    x = torch.FloatTensor(recent_sequence).unsqueeze(0).to(DEVICE)
    quantiles = model.predict_quantiles(x)
    return {k: v[0].tolist() for k, v in quantiles.items()}
