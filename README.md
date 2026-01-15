#  StreamRec  
**Production-Grade Real-Time MLOps Platform**

[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white)](https://mlflow.org/)
[![Feast](https://img.shields.io/badge/Feast-Feature_Store-orange?style=for-the-badge)](https://feast.dev/)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)

---


**StreamRec** is a fully containerized, production-grade **real-time MLOps platform** designed for **low-latency inference at scale**.

Although this repository demonstrates a **Recommendation System**, the same architecture works seamlessly for:

- Fraud Detection  
- Dynamic Pricing  
- Churn Prediction  
- Demand Forecasting  
- Any real-time ML workload  

The core idea is simple:

> **Train once. Serve anywhere. Never drift.**

StreamRec eliminates **training-serving skew** by using **Feast** for feature consistency and **MLflow** for model lifecycle management.

---

## System Architecture

StreamRec runs five decoupled microservices orchestrated with Docker Compose.

| Service | Technology | Role |
|--------|------------|------|
| Feature Store | Feast + Redis | Low-latency feature serving |
| Model Registry | MLflow + Postgres | Tracks models, metrics, versions |
| Artifact Store | MinIO (S3) | Stores trained model files |
| Prediction API | FastAPI | Real-time inference |
| Orchestrator | Docker Compose | Networking, volumes, startup |

---

##  Data Flow

### 1️. Training  
Historical features are loaded from Parquet, the model is trained and logged into **MLflow**, and the artifacts are stored in **MinIO**.

### 2️. Materialization  
Feast loads the latest feature values into **Redis** for real-time serving.

### 3️. Inference  
When a request arrives:
```text
Client → FastAPI → Feast (Redis) → MLflow Model → Prediction
```

No feature recomputation. No skew. One source of truth.

---
## Why StreamRec?

Most ML systems fail not because of bad models, but because of broken pipelines.

StreamRec solves the hardest production ML problems:

- Feature drift between training and inference  
- Unversioned models  
- Non-reproducible deployments  
- Slow real-time feature lookup  

This stack mirrors what large ML teams run in production:

**Feature Store → Model Registry → Artifact Store → Online Serving**.

---

## 📂 Project Structure

```text
stream-rec/
├── src/
│   ├── Dockerfile           # Definition for the API/Training container
│   ├── train_model.py       # Pipeline: Fetch Data -> Train -> Log to MLflow
│   ├── requirements.txt     # Python dependencies
│   └── ...
├── feature_repo/            # Feast Feature Store Definitions
│   ├── feature_store.yaml   # Connection config for Redis/Offline store
│   ├── definitions.py       # Feature definitions (Entities, Views)
│   └── data/                # Offline data source (Parquet files)
├── docker-compose.yml       # Infrastructure orchestration
└── README.md                # Documentation
```
---

##  Quick Start

### 1️. Prerequisites

- Docker Desktop (running)  
- Git  

---

### 2️. Clone & Launch

```bash
git clone https://github.com/YOUR_USERNAME/stream-rec.git
cd stream-rec
docker compose up -d --build
```

Wait ~30 seconds for all services to initialize.

---

### 3️. Initialize Feast

```bash
docker exec -w /app/feature_repo stream_rec_api feast apply
docker exec -w /app/feature_repo stream_rec_api feast materialize 2020-01-01 2026-01-01
```

---

### 4️. Train the Model
```bash
docker exec stream_rec_api python src/train_model.py
```
Expected output:

```text
✨ SUCCESS! Model saved to MLflow
```
---

### 5️. Run Inference
PowerShell:
```PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/predict" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{"user_id": 1}'
```
cURL / Bash:
```bash
Copy code
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1}'
```

---

## Customization

To use your own data:

### 1. Replace the .parquet files in

```text
feature_repo/data/
```
### 2. Update

```text
feature_repo/definitions.py
```
### 3. Update

```text
src/train_model.py
```
### 4. Re-run:

```bash
feast apply
feast materialize 2020-01-01 2026-01-01
python src/train_model.py
```
## Web Interfaces

#### MLflow -- http://localhost:5000

#### MinIO -- http://localhost:9001

#### FastAPI Docs -- http://localhost:8000/docs