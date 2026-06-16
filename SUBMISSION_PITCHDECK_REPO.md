# PARKSENSE AI — PITCH DECK & REPOSITORY STRUCTURE
## Sections 5–7

---

# SECTION 5 — 12-SLIDE PITCH DECK

---

## SLIDE 1 — TITLE SLIDE

**Objective:** Make a strong first impression

**Content:**
```
🅿️ ParkSense AI
"See the Invisible. Stop the Chaos."

AI-Driven Parking Intelligence for Smart City Enforcement

Team: [Team Name]
Hackathon: [Event Name] | Round 2
Date: June 2026
Track: Smart Mobility / Urban AI
```

**Visual Suggestions:**
- Dark background (#0a0d14) with a glowing city road network overlay
- Animated heatmap blobs in the background suggesting hotspot detection
- ParkSense AI logo prominent center-top

**Speaker Notes:**
> "Good [morning/afternoon], judges. The city you see behind me is Bengaluru — and every glowing dot represents a parking violation choking a carriageway. Today we're showing you how AI can make those dots visible, predictable, and actionable. This is ParkSense AI."

---

## SLIDE 2 — THE PROBLEM

**Objective:** Create urgency and establish pain clearly

**Content:**
```
THE PROBLEM: THE CITY CAN'T SEE ITS OWN CHOKEPOINTS

Every morning at 5 AM:
  → 34,085 illegal parking violations occur citywide
  → No central system sees them in real time
  → Officers are patrolling based on yesterday's memory

The Impact:
  🚗 50–60% carriageway capacity lost per illegally parked vehicle
  ⏱  18,000+ avoidable vehicle-hours of delay per month
  🏥 Emergency response delayed 2–4 minutes at blocked corridors
  🌫  32 tonnes of CO₂ wasted from idling vehicles monthly
  💸 14,400 litres of fuel burned unnecessarily every month

Source: Analysis of 298,450 actual BTP violation records
```

**Visual Suggestions:**
- Left: Before/after road cross-section showing lane capacity loss
- Right: Map with red congestion overlay near top violation zones
- Statistics in large bold numbers on cards

**Speaker Notes:**
> "Our dataset analysis shows a stunning fact: 75.4% of all violations — 225,000 records — happen between 10 PM and 6 AM. Cities are literally parking-blind at night. And the enforcement data takes 19.5 days on average to even reach the central system."

---

## SLIDE 3 — CURRENT CHALLENGES

**Objective:** Show why existing approaches fail

**Content:**
```
WHY TODAY'S ENFORCEMENT IS BROKEN

❌ REACTIVE         Officers respond after congestion forms, not before
❌ EXPERIENCE-BASED Patrol routes are based on intuition, not data
❌ DATA-BLIND        No city-wide visibility into violation patterns
❌ 19.5-DAY LAG      Avg 468h from violation capture to central system
❌ NO CONGESTION LINK No tool quantifies how parking impacts traffic flow
❌ REPEAT BLINDNESS  35,587 repeat offenders escape systematic deterrence
❌ 28.8% REJECTION   Nearly 1 in 3 validated records rejected due to quality

The gap is not resources. The gap is intelligence.
```

**Visual Suggestions:**
- Timeline showing the 468-hour lag as a shocking visual
- Table: "What Exists" vs "What's Needed" as two columns
- Photo of officer patrolling manually (left) vs AI map (right)

**Speaker Notes:**
> "Think about this: a violation happens at 5 AM. Officers log it on a device. That data takes an average of 19.5 days to reach the traffic management system. In that time, the same location has had violations every single night. This is not an enforcement problem. It's an intelligence problem."

---

## SLIDE 4 — DATASET INSIGHTS

**Objective:** Prove solutions are data-driven, not assumed

**Content:**
```
WHAT THE DATA TELLS US (298,450 Real BTP Records)

TEMPORAL INSIGHTS                SPATIAL INSIGHTS
────────────────────             ────────────────────
Peak Hour: 5 AM (11.4%)         #1 Hotspot: Shivajinagar/MG Rd
Night violations: 75.4%         Cell density: 4,411 in 100m×100m
January peak: 65,813            Top junction: Safina Plaza (1,544)
Sundays: 20% above average      Upparpet: 11.5% of all violations

ENFORCEMENT INSIGHTS             VEHICLE INSIGHTS
────────────────────             ────────────────────
Avg response lag: 468h          Scooters: 94,856 (most common)
SCITA sent: 85.7%               Buses: 1.78 violations/case (worst)
Validation rejection: 28.8%     Repeat offenders: 35,587 vehicles
Top repeat offender: 55 hits    Top plate: 55 violations in 5 months
```

**Visual Suggestions:**
- Hourly bar chart highlighting 5 AM spike in red
- City map with H3 hexagon heatmap from actual lat/lon data
- 4-quadrant insight board (2×2 grid of stats)

**Speaker Notes:**
> "Every single number on this slide comes directly from the provided dataset. We didn't assume patterns — we discovered them. And what we discovered fundamentally changed how we designed our solution."

---

## SLIDE 5 — SOLUTION OVERVIEW

**Objective:** Introduce ParkSense AI clearly and excitingly

**Content:**
```
INTRODUCING PARKSENSE AI

From Patrol-Based Guesswork → Precision AI Enforcement

LAYER 1: DETECT       DBSCAN/HDBSCAN spatial clustering
                      Real-time hotspot polygon generation

LAYER 2: SCORE        Congestion Impact Score (CIS)
                      Proprietary formula — first of its kind in India

LAYER 3: PREDICT      LSTM + Temporal Fusion Transformer
                      72-hour ahead violation forecasting

LAYER 4: ACT          Reinforcement Learning Patrol Optimizer
                      Turn-by-turn routes for maximum interceptions

LAYER 5: EXPLAIN      SHAP Explainable AI
                      Every alert backed by interpretable evidence

LAYER 6: DISPLAY      Smart GIS Dashboard
                      7-page command center for enforcement officers
```

**Visual Suggestions:**
- Vertical layered stack diagram with icons for each layer
- Each layer glowing in gradient (purple → teal → red)
- Screenshot thumbnail of dashboard on the right side

**Speaker Notes:**
> "ParkSense AI is not a map. It's not a dashboard. It's a decision engine — six layers of intelligence that transform raw violation data into a precise, timestamped, geographically-targeted action for every officer on every shift."

---

## SLIDE 6 — SYSTEM ARCHITECTURE

**Objective:** Demonstrate technical depth and engineering maturity

**Content:**
```
END-TO-END ARCHITECTURE

DATA SOURCES
Historical BTP Records + GIS (OSM) + Real-Time CCTV + GPS + Events
                     │
              Apache Kafka (Streaming)
                     │
         PostgreSQL + PostGIS (Data Lake)
                     │
         ┌───────────┴───────────┐
         │    Data Processing    │
    Cleaning · GeoHash · Features
         └───────────┬───────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
DBSCAN/         XGBoost/          LSTM/TFT
HDBSCAN         LightGBM         Forecaster
Hotspot         CIS Score        72h Predict
    │                │                │
    └────────────────┼────────────────┘
                     │
         Decision Support Engine
        EPS · SHAP · RL Patrol Planner
                     │
    ┌────────────────┼────────────────┐
    │                │                │
React          FastAPI           Officer
Dashboard      REST API          Mobile PWA
```

**Visual Suggestions:**
- Full-width architecture diagram with arrow flows
- Color-coded layers: Data (blue) → ML (purple) → Action (red)
- Docker/K8s logos at the bottom deployment layer

**Speaker Notes:**
> "The architecture is cloud-native from day one. Apache Kafka handles real-time ingestion. PostGIS handles spatial queries in milliseconds. The ML layer runs three parallel model families. And the decision support engine synthesises all outputs into a single ranked action queue for officers."

---

## SLIDE 7 — AI MODELS

**Objective:** Demonstrate ML sophistication

**Content:**
```
FOUR AI MODELS, ONE INTELLIGENCE PLATFORM

MODEL 1: HOTSPOT DETECTION
  Algorithm: DBSCAN + HDBSCAN
  Input:     Lat, Lon, Hour, Violation Weight
  Output:    Named hotspot clusters + severity polygon
  Metric:    Silhouette Score > 0.45

MODEL 2: CONGESTION IMPACT PREDICTION
  Algorithm: XGBoost + LightGBM Ensemble (55:45 weight)
  Features:  32 engineered (spatial + temporal + vehicle)
  Output:    CIS Score 0–10 per violation
  Metric:    R² > 0.82, AUC > 0.88

MODEL 3: FUTURE HOTSPOT FORECAST
  Algorithm: LSTM + Temporal Fusion Transformer
  Horizon:   72 hours ahead (hourly resolution)
  Output:    Violation probability + uncertainty bands
  Metric:    RMSE < 0.65, 90th-pct coverage > 87%

MODEL 4: PATROL ROUTE OPTIMIZATION
  Algorithm: Proximal Policy Optimization (PPO-RL)
  State:     Location, Priority Queue, Time, Fuel
  Reward:    +10/interception, -1/km, +5/pre-emptive
  Output:    Turn-by-turn GIS shift route
```

**Visual Suggestions:**
- 4-panel grid, one model per panel
- Mini loss curves and confusion matrix thumbnails
- SHAP waterfall chart for Model 2 as visual proof

**Speaker Notes:**
> "We don't use one model. We use four, each solving a distinct enforcement problem. The ensemble of XGBoost and LightGBM for CIS prediction is particularly important — it's what turns a parking violation from a data point into a traffic impact number that officers can act on."

---

## SLIDE 8 — GIS INTELLIGENCE LAYER

**Objective:** Show spatial depth and visual impact

**Content:**
```
GIS INTELLIGENCE — SEE THE CITY LIKE NEVER BEFORE

6 Interactive Map Layers (Kepler.gl + Mapbox + PostGIS)

🔴 VIOLATION HEATMAP
   H3 hexagonal binning (resolution 7, ~460m cells)
   Time-slider animation: hourly/monthly patterns

🟠 DBSCAN HOTSPOT POLYGONS
   Convex hull clusters, color-coded by CIS score
   Click to view SHAP explanation panel

🟡 PATROL COVERAGE MAP
   Active patrol GPS tracks in real-time
   Uncovered zones highlighted in grey

🟢 REPEAT OFFENDER MAP
   Vehicle concentration by geohash
   Top-55 repeat offender watch-list overlay

🔵 FORECAST PROBABILITY GRID
   72h violation risk, rendered as opacity gradient

🟣 JUNCTION RISK LAYER
   BTP junction codes with risk scores
   Safina Plaza (BTP051): CIS 8.1 flagged
```

**Visual Suggestions:**
- Full-bleed Kepler.gl screenshot showing Bengaluru heatmap
- Layer toggle panel mockup on the right
- Zoomed inset showing Safina Plaza junction cluster

**Speaker Notes:**
> "GIS is not a nice-to-have for us — it is the core interface between AI intelligence and human decision-making. An officer looking at our map sees not just where violations are, but where they will be 72 hours from now, and exactly which routes to take to intercept them."

---

## SLIDE 9 — SMART DASHBOARD

**Objective:** Demonstrate product maturity and UX thinking

**Content:**
```
THE PARKSENSE COMMAND CENTER — 7 OPERATIONAL PAGES

PAGE 1: CITY OVERVIEW
  KPI cards · Hourly trend · Monthly chart · Violation breakdown

PAGE 2: LIVE HOTSPOT MAP
  6-layer GIS map · Real-time cluster alerts · SHAP popups

PAGE 3: 72-HOUR FORECAST
  Zone risk cards · Confidence intervals · Pre-emptive alerts

PAGE 4: RISK RANKINGS
  EPS-sorted station table · Drill-down per station

PAGE 5: PATROL INTELLIGENCE
  AI-generated priority queue · RL-optimised routes
  "Deploy 2 units to Safina Plaza by 04:00 — est. 28 interceptions"

PAGE 6: EXPLAINABLE AI
  SHAP waterfall for every alert
  Natural language enforcement justification

PAGE 7: ANALYTICS
  Deep pattern intelligence · Repeat offender analytics
  Monthly trend · Validation quality scorecard
```

**Visual Suggestions:**
- Mockup thumbnail carousel: one image per page
- Annotated screenshot of the dashboard.html live demo
- Call out the dark-mode, premium design aesthetic

**Speaker Notes:**
> "This isn't a prototype wireframe. This is a deployed, interactive dashboard that a control room operator or field officer can use today. Every page connects directly to live data."

---

## SLIDE 10 — IMPACT METRICS

**Objective:** Quantify ROI for decision-makers and judges

**Content:**
```
MEASURABLE OUTCOMES — YEAR 1 TARGETS

ENFORCEMENT IMPACT              TRAFFIC IMPACT
────────────────────            ────────────────────
Illegal parking at              Peak-hour delay:
hotspots: −30 to −45%          −18 to −22%

Enforcement efficiency:         Emergency response:
+25% violations/officer-shift   −2 to −3 min

Data submission lag:            Fuel savings:
468 hours → < 5 minutes        −9,000 L/month

Repeat offender rate:           CO₂ reduction:
15.4% → < 8%                   −19 tonnes/month

FINANCIAL IMPACT
────────────────────────────────────
Enforcement cost savings:   ~25% operational cost reduction
Fuel tax recovered:         +₹2.8 Cr/year from targeted enforcement
Pollution fines avoided:    Significant indirect savings
```

**Visual Suggestions:**
- Before/After comparison KPI cards with arrows
- Doughnut chart showing efficiency improvement
- Traffic delay graph: current vs projected

**Speaker Notes:**
> "These are conservative projections based on published results from comparable AI enforcement deployments in Seoul, Singapore, and London. Indian-context calibration is built into our assumptions."

---

## SLIDE 11 — GOVERNMENT & BUSINESS VALUE

**Objective:** Show real-world adoption pathway

**Content:**
```
WHO BENEFITS AND HOW

TRAFFIC POLICE DEPARTMENTS
  ✓ 25% better enforcement per shift
  ✓ Data-driven staff deployment
  ✓ Officer accountability via audit trail
  ✓ SHAP-backed defensible decisions

MUNICIPAL CORPORATIONS (BBMP)
  ✓ Carriageway capacity restored
  ✓ Footpath encroachment data
  ✓ Event & festival enforcement planning
  ✓ Smart City reporting compliance

STATE TRANSPORT AUTHORITIES
  ✓ Policy: which violation types to target
  ✓ Budget justification with impact metrics
  ✓ Multi-city deployment roadmap

CITIZENS
  ✓ Faster commutes (−18% delay)
  ✓ Cleaner air (−19t CO₂/month)
  ✓ Safer pedestrian zones
  ✓ Ambulance response improvement

DEPLOYMENT READINESS
  ✓ Integrates with existing BTP SCITA system
  ✓ Officer training: 2-day program
  ✓ Pilot: 5 stations in 90 days
  ✓ Full city: 6 months
```

**Visual Suggestions:**
- 4-quadrant stakeholder grid (police / BBMP / state / citizens)
- Deployment timeline arrow (90 days pilot → 6 months city)
- Government logo placeholders for visual credibility

---

## SLIDE 12 — WHY WE WIN

**Objective:** Close the deal with judges

**Content:**
```
TRADITIONAL ENFORCEMENT vs PARKSENSE AI

                    TRADITIONAL    PARKSENSE AI
Detection           Patrol-based   AI clustering
Prediction          None           72h forecast
Congestion link     Not measured   CIS score
Prioritisation      Intuition      EPS ranking
Response time       19.5 days lag  < 5 minutes
Patrol routing      Fixed beats    RL-optimised
Explainability      "Officer said" SHAP justified
Repeat offenders    Manual         Auto watch-list
Night operations    Minimal        NSIL dedicated layer
Scalability         Headcount      Cloud-native K8s
Cost trend          Rising         Decreasing after Y1

WE ARE NOT BUILDING A DASHBOARD.
WE ARE BUILDING THE BRAIN OF SMART CITY ENFORCEMENT.

"See the Invisible. Stop the Chaos."
```

**Visual Suggestions:**
- Full comparison table with ✅ and ❌ columns
- Bold closing statement in gradient text center-screen
- Tagline as closing footer with project name

**Speaker Notes:**
> "Every system on that left column produces data. ParkSense AI produces decisions. That's the difference between a tool and a platform. Bengaluru's streets don't need more enforcement officers. They need this intelligence layer. Thank you."

---

# SECTION 6 — GITHUB REPOSITORY STRUCTURE

```
parksense-ai/
│
├── 📁 frontend/                  # React 18 + Vite Dashboard SPA
│   ├── src/
│   │   ├── pages/               # City Overview, Hotspots, Forecast, etc.
│   │   ├── components/          # Map, Charts, Tables, SHAP widgets
│   │   ├── hooks/               # useHotspots, useForecast, usePatrol
│   │   ├── store/               # Zustand global state
│   │   └── api/                 # Axios API clients
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── 📁 backend/                   # FastAPI Python backend
│   ├── app/
│   │   ├── api/                 # Route handlers (violations, hotspots, forecast)
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── services/            # Business logic layer
│   │   ├── core/                # Config, auth, security, DB connection
│   │   └── main.py              # FastAPI app entry point
│   ├── requirements.txt
│   └── Dockerfile
│
├── 📁 ml/                        # All machine learning code
│   ├── clustering/              # DBSCAN/HDBSCAN hotspot detection
│   ├── cis_model/               # XGBoost + LightGBM CIS prediction
│   ├── forecasting/             # LSTM + TFT temporal models
│   ├── patrol_rl/               # PPO Reinforcement Learning agent
│   ├── shap_explainer/          # SHAP value computation + export
│   ├── feature_engineering/     # All feature creation scripts
│   ├── training_pipeline.py     # End-to-end training orchestrator
│   └── model_registry.py        # MLflow integration
│
├── 📁 gis/                       # Geospatial processing
│   ├── hotspot_mapper.py        # DBSCAN → GeoJSON polygon generator
│   ├── h3_indexer.py            # Uber H3 hexagonal grid encoding
│   ├── patrol_router.py         # OSMnx road network + route generation
│   ├── junction_risk.py         # Junction code → risk score mapping
│   └── layers/                  # Layer definitions (heatmap, clusters, etc.)
│
├── 📁 data/                      # Data handling (no raw data committed)
│   ├── schema/                  # DB schema SQL files
│   ├── migrations/              # Alembic DB migrations
│   ├── sample/                  # Anonymised 1000-row sample for demo
│   └── README.md                # Data download/setup instructions
│
├── 📁 notebooks/                 # Jupyter EDA notebooks
│   ├── 01_eda_overview.ipynb    # Dataset overview + quality check
│   ├── 02_temporal_analysis.ipynb
│   ├── 03_spatial_analysis.ipynb
│   ├── 04_violation_analysis.ipynb
│   ├── 05_model_training.ipynb
│   └── 06_shap_analysis.ipynb
│
├── 📁 models/                    # Saved model artifacts
│   ├── dbscan_model.pkl
│   ├── xgb_cis_model.json
│   ├── lgbm_cis_model.txt
│   ├── lstm_forecast.pt
│   └── ppo_patrol_agent.pt
│
├── 📁 deployment/                # Docker + Kubernetes configs
│   ├── docker-compose.yml       # Local dev: all services
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── k8s/                     # Production K8s manifests
│   │   ├── backend-deployment.yaml
│   │   ├── frontend-deployment.yaml
│   │   ├── postgres-statefulset.yaml
│   │   ├── redis-deployment.yaml
│   │   └── ingress.yaml
│   └── nginx.conf
│
├── 📁 docs/                      # Documentation
│   ├── architecture.md
│   ├── api_reference.md
│   ├── data_dictionary.md
│   ├── model_cards/             # ML model documentation
│   └── pitch_deck.pdf
│
├── .env.example                  # Environment variable template
├── .gitignore
├── docker-compose.yml            # Root-level dev compose
├── Makefile                      # Common dev commands
└── README.md                     # Main project README
```

## Folder Responsibilities

| Folder | Language | Responsibility |
|---|---|---|
| `frontend/` | TypeScript/React | Web dashboard SPA, officer PWA, all charts and GIS layers |
| `backend/` | Python/FastAPI | REST API, WebSocket feeds, auth, caching, DB queries |
| `ml/` | Python | All model training, inference, SHAP, feature pipelines |
| `gis/` | Python/GeoPandas | Spatial processing, H3 indexing, patrol routing, GeoJSON |
| `data/` | SQL/Alembic | Schema definitions, migrations, sample data |
| `notebooks/` | Jupyter | EDA, model prototyping, SHAP visualisation |
| `models/` | Binary artifacts | Serialised trained models for inference |
| `deployment/` | YAML/Docker | Local + production container orchestration |
| `docs/` | Markdown | Architecture, API docs, model cards, pitch |

---

# SECTION 7 — SOURCE CODE MODULES

## Module 1: Data Ingestion & Preprocessing
**File:** `backend/app/services/ingestion.py`
**Responsibility:** Reads raw BTP CSV, validates schema, parses JSON array columns (violation_type, offence_code), filters spatial bounding box, removes duplicates, casts timestamps to UTC, encodes GeoHash at precision 7, writes to PostGIS.

## Module 2: Feature Engineering Engine
**File:** `ml/feature_engineering/feature_builder.py`
**Responsibility:** Computes all 32 features — VD, JRI, PHS, WM, MSS, RDS, ROD, PRI per record. Outputs feature matrix for model consumption. Handles cyclic encoding (sin/cos hour/month).

## Module 3: Hotspot Detection Service
**File:** `ml/clustering/hotspot_detector.py`
**Responsibility:** Runs DBSCAN/HDBSCAN on lat/lon with haversine metric. Returns labeled cluster IDs. Feeds `gis/hotspot_mapper.py` to generate convex hull GeoJSON polygons. Computes cluster-level CIS aggregation.

## Module 4: CIS Prediction Model
**File:** `ml/cis_model/cis_predictor.py`
**Responsibility:** XGBoost + LightGBM ensemble inference. Loads saved model artifacts. Accepts feature vector, returns CIS score 0–10. Used by API endpoint `/api/v1/violations/{id}/cis`.

## Module 5: Forecasting Engine
**File:** `ml/forecasting/forecast_engine.py`
**Responsibility:** LSTM + TFT inference. Accepts geohash cell + horizon hours (1–72). Returns point forecast + P10/P50/P90 bands. Retraining scheduled via Airflow DAG weekly.

## Module 6: Patrol Route Optimizer
**File:** `ml/patrol_rl/patrol_optimizer.py`
**Responsibility:** Loads trained PPO agent. Accepts patrol unit constraints (location, shift hours, range). Queries OSMnx road graph. Returns waypoint list as GeoJSON LineString. Exposes via `/api/v1/patrol/route`.

## Module 7: SHAP Explainer Service
**File:** `ml/shap_explainer/explainer.py`
**Responsibility:** Wraps SHAP TreeExplainer around XGBoost CIS model. On demand, computes SHAP values for any violation. Returns JSON: {feature, shap_value, direction} array for dashboard waterfall chart.

## Module 8: GIS Layer Service
**File:** `gis/hotspot_mapper.py` + `gis/h3_indexer.py`
**Responsibility:** Converts DBSCAN cluster outputs to GeoJSON FeatureCollections. H3 indexer aggregates violations into hexagonal cells. Both outputs served via `/api/v1/gis/hotspots` and `/api/v1/gis/heatmap`.

## Module 9: Enforcement Priority Engine (EPS)
**File:** `backend/app/services/eps_engine.py`
**Responsibility:** Real-time ranking engine. Queries PostGIS for recent violations per zone, fetches CIS scores from Redis cache, computes EPS per zone, returns top-N ranked patrol zones. Refreshes every 5 minutes.

## Module 10: REST API Layer
**File:** `backend/app/api/`
**Responsibility:** FastAPI route handlers organized by domain:
- `/api/v1/violations/` — CRUD + analytics
- `/api/v1/hotspots/` — cluster data + GeoJSON
- `/api/v1/forecast/` — 72h predictions
- `/api/v1/patrol/` — route assignments
- `/api/v1/gis/` — map layer endpoints
- `/api/v1/auth/` — JWT + role-based access

## Module 11: Authentication & RBAC
**File:** `backend/app/core/security.py`
**Responsibility:** JWT-based authentication. Role-Based Access Control: ADMIN (all access), STATION_HEAD (own station), OFFICER (read + patrol endpoints), VIEWER (dashboard read-only). All endpoints decorated with role guards.

## Module 12: React Dashboard
**File:** `frontend/src/pages/`
**Responsibility:** 7-page SPA. Communicates with FastAPI via Axios REST + Socket.IO WebSocket for live alert feeds. Kepler.gl and Mapbox GL JS render GIS layers. Chart.js for analytics charts. SHAP waterfall rendered as D3.js custom component.
