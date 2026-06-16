# ParkSense AI 🅿️

> **"See the Invisible. Stop the Chaos."**
> AI-Driven Parking Intelligence for Smart City Enforcement

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-green.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-teal.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2-blue.svg)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

---

## 📌 Project Overview

ParkSense AI is a next-generation **AI Parking Intelligence Platform** that transforms raw parking violation records into precision enforcement intelligence. Built for urban traffic police departments and smart city command centers, it solves the core problem of **parking-induced congestion** by moving enforcement from reactive patrol to predictive, data-driven decision-making.

Developed based on analysis of **298,450 real BTP violation records** from Bengaluru (Nov 2023–Apr 2024), ParkSense AI reveals that:
- **75.4%** of violations occur between 10 PM and 6 AM — enforcement is misaligned
- The average data submission lag is **468 hours (19.5 days)** — making the system forensic, not operational
- A single grid cell near MG Road accumulated **4,411 violations** in a ~100m radius
- **35,587 repeat offenders** (15.4%) systematically escape deterrence

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔵 **Hotspot Detection** | DBSCAN/HDBSCAN spatial clustering with real-time GeoJSON polygon output |
| 📊 **Congestion Impact Score** | Proprietary CIS formula quantifying traffic degradation per violation (0–10) |
| 🔮 **72h Forecasting** | LSTM + Temporal Fusion Transformer predicting violations 72 hours ahead |
| 🚔 **Patrol Optimization** | Reinforcement Learning (PPO) generating optimal shift routes per officer |
| 🧠 **Explainable AI** | SHAP-backed natural language justification for every alert |
| 🗺 **GIS Intelligence** | 6-layer interactive map (Kepler.gl + Mapbox): heatmap, clusters, patrol, junctions |
| 📱 **Officer PWA** | Mobile-first Progressive Web App for field officers |
| 🔔 **Live Alert Feed** | WebSocket real-time enforcement priority queue |

---

## 🏗 Architecture

```
Data Sources → Kafka → PostgreSQL+PostGIS → Feature Engineering
    → DBSCAN/HDBSCAN · XGBoost/LightGBM · LSTM/TFT · PPO-RL
    → Decision Support (CIS + EPS + SHAP)
    → React Dashboard · FastAPI · Officer PWA
```

Full architecture diagram: [docs/architecture.md](docs/architecture.md)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker Desktop
- PostgreSQL 15 + PostGIS 3.3

### 1-Command Docker Launch (Recommended)
```bash
git clone https://github.com/your-org/parksense-ai.git
cd parksense-ai
cp .env.example .env          # Edit with your credentials
docker-compose up --build     # Launches all services
```
Open **http://localhost:3000** for the dashboard.

### Manual Setup
```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev

# ML Pipeline
cd ml && python training_pipeline.py --config configs/default.yaml
```

Full instructions: [INSTRUCTIONS_TO_RUN.md](INSTRUCTIONS_TO_RUN.md)

---

## 📸 Screenshots

| Dashboard Page | Preview |
|---|---|
| City Overview | `docs/screenshots/overview.png` |
| Live Hotspot Map | `docs/screenshots/hotspots.png` |
| 72h Forecast Panel | `docs/screenshots/forecast.png` |
| Patrol Intelligence | `docs/screenshots/patrol.png` |
| Explainable AI (SHAP) | `docs/screenshots/xai.png` |

> 💡 Open `dashboard.html` directly in any browser for a live demo — no server required.

---

## 📁 Folder Structure

```
parksense-ai/
├── frontend/          # React 18 + Vite dashboard SPA
├── backend/           # FastAPI REST + WebSocket API
├── ml/                # All ML models (clustering, CIS, forecast, RL)
├── gis/               # GeoPandas, H3 indexing, patrol routing
├── data/              # Schema, migrations, sample data
├── notebooks/         # Jupyter EDA notebooks (6 notebooks)
├── models/            # Saved model artifacts (pkl, json, pt)
├── deployment/        # Docker + Kubernetes configs
├── docs/              # Architecture, API reference, model cards
├── dashboard.html     # Standalone demo (no server needed)
└── README.md
```

---

## 🛠 Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Frontend** | React + Vite | 18.2 / 5.0 | Dashboard SPA |
| **Maps** | Kepler.gl + Mapbox GL JS | Latest | GIS layers |
| **Charts** | Chart.js | 4.4 | Analytics visualizations |
| **API** | FastAPI | 0.104 | REST + WebSocket |
| **Auth** | JWT + RBAC | — | Role-based access |
| **ML — Clustering** | DBSCAN, HDBSCAN | sklearn 1.3 | Hotspot detection |
| **ML — Regression** | XGBoost, LightGBM | 2.0, 4.1 | CIS prediction |
| **ML — Forecast** | PyTorch LSTM, TFT | 2.1 | 72h prediction |
| **ML — RL** | Stable-Baselines3 PPO | 2.2 | Patrol routing |
| **XAI** | SHAP | 0.43 | Explainability |
| **GIS** | GeoPandas, PostGIS | 0.14, 3.3 | Spatial processing |
| **Spatial Index** | Uber H3 | 3.7 | Hexagonal binning |
| **Road Network** | OSMnx | 1.6 | OpenStreetMap graph |
| **Database** | PostgreSQL + PostGIS | 15 + 3.3 | Primary data store |
| **Cache** | Redis | 7.2 | Query + session cache |
| **Streaming** | Apache Kafka | 3.5 | Real-time ingestion |
| **MLOps** | MLflow | 2.8 | Model registry |
| **Orchestration** | Apache Airflow | 2.7 | DAG scheduling |
| **Containers** | Docker + Kubernetes | 24 + 1.28 | Deployment |

---

## 🔬 AI Models

### 1. Hotspot Detection (DBSCAN + HDBSCAN)
- **Input:** `(lat, lon, hour, violation_weight)`
- **Output:** GeoJSON cluster polygons with CIS score
- **Metric:** Silhouette Score > 0.45

### 2. Congestion Impact Score — XGBoost + LightGBM Ensemble
- **Features:** 32 engineered (spatial + temporal + vehicle + historical)
- **Output:** CIS score 0–10 per violation
- **Metric:** R² > 0.82, AUC > 0.88

### 3. 72-Hour Forecasting — LSTM + TFT
- **Input:** 168-hour rolling violation history per geohash
- **Output:** 72-step ahead prediction + P10/P50/P90 bands
- **Metric:** RMSE < 0.65, 90th-pct coverage > 87%

### 4. Patrol Route Optimizer — PPO Reinforcement Learning
- **State:** Location, priority queue, time remaining, fuel
- **Reward:** +10/interception, −1/km, +5/pre-emptive arrival
- **Output:** Turn-by-turn GIS shift route (GeoJSON LineString)

---

## 🚀 Future Work

- [ ] Real-time CCTV integration (YOLOv8 vehicle detection)
- [ ] WhatsApp/SMS officer alert integration
- [ ] Multi-language support (Kannada, Hindi, Tamil)
- [ ] ANPR (Automatic Number Plate Recognition) module
- [ ] State-level federated deployment (Karnataka pilot)
- [ ] Weather-adjusted violation prediction
- [ ] Court-ready digital challan trail with blockchain audit log

---

## 📋 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

## 👥 Contributors

| Name | Role |
|---|---|
| [Team Member 1] | ML Engineer — Hotspot Detection, CIS Model |
| [Team Member 2] | Backend Engineer — FastAPI, PostGIS |
| [Team Member 3] | Frontend Engineer — React Dashboard, GIS Layers |
| [Team Member 4] | Data Scientist — EDA, Feature Engineering |

---

## 🏆 Hackathon Submission

- **Problem Statement:** Poor Visibility on Parking-Induced Congestion
- **Event:** [Hackathon Name] — Round 2
- **Track:** Smart Mobility / Urban AI
- **Dataset:** BTP Bengaluru Violation Records (298,450 records, Nov 2023–Apr 2024)

> *"Bengaluru's streets don't need more officers. They need smarter decisions."*
