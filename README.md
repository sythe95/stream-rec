# 🚀 StreamRec 3.0
**Enterprise-Grade Real-Time MLOps & Streaming Platform**

[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Redpanda](https://img.shields.io/badge/Redpanda-231F20?style=for-the-badge&logo=redpanda&logoColor=white)](https://redpanda.com/)
[![Apache Spark](https://img.shields.io/badge/Apache_Spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Feast](https://img.shields.io/badge/Feast-Feature_Store-orange?style=for-the-badge)](https://feast.dev/)
[![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white)](https://mlflow.org/)
[![MinIO](https://img.shields.io/badge/MinIO-00B4E0?style=for-the-badge&logo=minio&logoColor=white)](https://min.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)](https://grafana.com/)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)

---

**StreamRec 3.0** is a fully containerized, production-grade **real-time MLOps platform** utilizing a Lambda architecture to deliver **low-latency inference at scale**.

Version 3.0 represents a massive evolution from a monolithic script to a decoupled microservice architecture. It introduces **Apache Spark** for distributed stream processing, full SRE observability with **Prometheus & Grafana**, and automated CI/CD pipelines via **GitHub Actions**.

The core philosophy of StreamRec:
> **Train on history. React in real-time. Never drift.**

---

## 🏗️ Architecture Overview

StreamRec 3.0 follows a **decoupled microservice architecture** orchestrated using Docker Compose. Each component is independently deployable and communicates through well-defined interfaces, enabling scalability, fault isolation, and easier extensibility.

| Component           | Technology              | Role                                                                 |
|--------------------|------------------------|----------------------------------------------------------------------|
| Message Broker     | Redpanda (Kafka API)   | High-throughput, low-latency event streaming backbone                |
| Stream Processor   | Apache Spark (PySpark) | Distributed real-time feature computation                            |
| Feature Store      | Feast + Redis          | Online feature serving with millisecond latency                      |
| Model Registry     | MLflow + Postgres      | Experiment tracking and versioned model management                   |
| Artifact Store     | MinIO (S3-compatible)  | Storage for serialized model artifacts and data                      |
| Prediction API     | FastAPI                | Real-time inference service                                          |
| Observability      | Prometheus + Grafana   | Metrics collection and visualization (Four Golden Signals)           |
| CI/CD              | GitHub Actions         | Automated linting, build validation, and workflow automation         |

This architecture separates **data ingestion**, **feature computation**, **model management**, and **inference serving**, allowing each layer to evolve independently without impacting the entire system.

The system is designed to handle:
- Continuous event streams
- Real-time feature updates
- Low-latency inference requests
- Production-grade monitoring and debugging

---

## 🌊 Data Flow (Lambda Architecture)

StreamRec 3.0 follows a **Lambda architecture**, combining batch and streaming pipelines to ensure both accuracy (from historical data) and freshness (from real-time events).

The system operates across three coordinated layers:

---

### 1️⃣ Batch Pipeline (Offline Training)

- Historical data is loaded from Parquet files
- Features are computed and used to train ML models
- Models are tracked and versioned in MLflow
- Serialized artifacts are stored in MinIO (S3-compatible storage)
- Feast materializes baseline features into the Redis online store

This layer provides **stable, high-quality baseline features** derived from complete historical data.

---

### 2️⃣ Streaming Pipeline (Real-Time Updates)

- **Producer (`event_simulator`)** generates live user interaction events
- Events are published to Redpanda (Kafka-compatible broker)
- **Consumer (`stream_processor`)** uses PySpark Structured Streaming to:
  - Process events in near real-time
  - Compute rolling and incremental features across distributed nodes
- Updated features are pushed into Redis via Feast PushSource

This layer ensures **features are continuously updated** as new events arrive, overriding stale batch values.

---

### 3️⃣ Real-Time Inference Layer

- FastAPI exposes a `/predict` endpoint
- On each request:
  - Latest features are fetched from Redis (Feast online store)
  - Model artifacts are loaded from MinIO
  - Prediction is generated dynamically

This guarantees that inference always uses the **most recent feature state**, not just precomputed batch data.

---

### 🔁 Key Principle

> Batch provides completeness. Streaming provides freshness.  
> Together, they ensure accurate and up-to-date predictions.

---

### ⚡ End-to-End Flow Summary

1. Train model on historical data → store in MLflow + MinIO  
2. Materialize baseline features → Redis via Feast  
3. Stream live events → Redpanda  
4. Process streams → Spark updates features  
5. Push updates → Redis (override batch values)  
6. Serve predictions → FastAPI using latest features  

The result is a system where predictions **evolve in real time** as user behavior changes.

---

## 📊 Observability & SRE

StreamRec 3.0 includes built-in observability to monitor system health, performance, and reliability in real time. The platform follows industry-standard SRE practices by exposing and tracking the **Four Golden Signals**: traffic, latency, errors, and saturation (approximated via system behavior).

### 🔍 Metrics Collection

- FastAPI services are instrumented using `prometheus-fastapi-instrumentator`
- Prometheus scrapes application metrics at regular intervals (default: 5s)
- Metrics include:
  - Request throughput (requests/sec)
  - Response latency (P50, P95)
  - HTTP status codes (2xx, 4xx, 5xx)
  - Exception counts

### 📈 Visualization (Grafana Dashboards)

Grafana provides real-time dashboards to monitor system behavior:

- **Traffic** → Request rate over time  
- **Latency** → P95 response times (target: sub-100ms)  
- **Errors** → Failure rates and exception tracking  
- **Status Codes** → Distribution of API responses  

Dashboards are version-controlled under `dashboards/` and can be treated as **“Dashboards as Code”**, making them reproducible and portable.

### 🚨 Why This Matters

- Detect performance regressions early  
- Identify failing components in a distributed system  
- Validate system behavior under load (e.g., during stress testing)  
- Provide visibility into real-time inference performance  

This ensures StreamRec is not just functional, but **observable, debuggable, and production-aware**.

---

## 📂 Project Structure

StreamRec 3.0 is organized as a **modular microservice-based repository**, where each component is isolated and independently deployable.

```text
stream-rec/
├── .github/workflows/     # CI/CD pipelines (GitHub Actions)
├── dashboards/            # Grafana dashboards (JSON, version-controlled)
├── feature_repo/          # Feast feature definitions and configs
├── prometheus/            # Prometheus scraping configuration
├── services/              # Core microservices
│ ├── event_simulator/     # Generates streaming events (Kafka producer)
│ ├── inference_api/       # FastAPI service for real-time predictions
│ └── stream_processor/    # PySpark streaming consumer
├── training/              # Offline training pipeline (MLflow integration)
├── docker-compose.yml     # Multi-service orchestration
└── Makefile               # Developer commands (build, run, test)
```
### 🧩 Design Principles

- **Separation of Concerns**  
  Each service handles a single responsibility (ingestion, processing, serving)

- **Loose Coupling**  
  Services communicate via Redpanda (Kafka), not direct dependencies

- **Reproducibility**  
  Infrastructure and dashboards are version-controlled

- **Developer Experience**  
  Common workflows are abstracted via `Makefile` commands

---

> Note: If legacy directories (e.g., `src/`) exist, they are being phased out in favor of this service-oriented structure.
---

## 🚀 Quick Start

Get StreamRec 3.0 running locally in a few minutes.

### ⚙️ Prerequisites

Make sure you have the following installed:

- Docker & Docker Compose
- GNU Make
- (Recommended) ≥ 8GB RAM for smooth multi-container execution

---

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/sythe95/stream-rec.git
cd stream-rec
```

### 2️⃣ Start Infrastructure

Spin up all core services (Postgres, MinIO, Redis, Redpanda, Prometheus, Grafana):
```bash
make up
```
Wait ~30–60 seconds for all containers to initialize.

### 3️⃣ Train Model & Materialize Features
```bash
make train
```
This will:

- Train the ML model on historical data

- Register the model in MLflow

- Store artifacts in MinIO

- Materialize baseline features into Redis via Feast

### 4️⃣ Start Real-Time Pipeline

Open two terminals:

**Terminal A — Event Producer**
```bash
make producer
```
**Terminal B — Stream Processor (Spark)**
```bash
make consumer
```
### 5️⃣ Test Real-Time Inference

Send prediction requests:
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1}'
```
(Optional) Simulate load:
```bash
while true; do
  curl -s -X POST "http://localhost:8000/predict" \
       -H "Content-Type: application/json" \
       -d '{"user_id": 1}' > /dev/null
done
```
### 6️⃣ Tear Down
```bash
make down
```
Note: Persistent volumes (e.g., Grafana dashboards) are retained across runs.

---

## 🌐 Web Interfaces

Once the system is running, you can access the following services:

| Service        | URL                          | Description                          | Credentials        |
|----------------|------------------------------|--------------------------------------|--------------------|
| Grafana        | http://localhost:3000        | Metrics dashboards (Golden Signals)  | admin / admin      |
| Prometheus     | http://localhost:9090        | Raw metrics and query interface      | —                  |
| MLflow         | http://localhost:5000        | Experiment tracking & model registry | —                  |
| MinIO Console  | http://localhost:9001        | Object storage (S3-compatible)       | minio / minio123   |
| FastAPI Docs   | http://localhost:8000/docs   | API documentation (Swagger UI)       | —                  |

---

### 🧭 How to Use

- **Grafana** → Monitor traffic, latency, and errors in real time  
- **Prometheus** → Run custom metric queries (PromQL)  
- **MLflow** → Compare experiments and inspect model versions  
- **MinIO** → Browse stored model artifacts and data  
- **FastAPI Docs** → Test `/predict` interactively  

---

> Note: These are default local development credentials and configurations.