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

## 🏗️ System Architecture

StreamRec runs a highly decoupled microservice stack orchestrated via Docker Compose.


| Component          | Technology                  | Role |
|--------------------|-----------------------------|------|
| **Message Broker** | Redpanda (Kafka)            | High-throughput, low-latency event streaming |
| **Stream Processor** | Apache Spark (PySpark)    | Calculates distributed rolling ML features in real-time |
| **Feature Store**  | Feast + Redis               | Low-latency feature serving via PushSource |
| **Model Registry** | MLflow + Postgres           | Tracks models, metrics, and versions |
| **Artifact Store** | MinIO (S3)                  | Stores serialized Scikit-Learn model artifacts |
| **Prediction API** | FastAPI                     | Serves dynamic, real-time inferences |
| **Observability**  | Prometheus + Grafana        | Scrapes metrics and visualizes the "Four Golden Signals" |
| **CI/CD**          | GitHub Actions              | Automated linting and Docker build verification |

---

## 🌊 Data Flow (The Lambda Architecture)

### 1️⃣ The Batch Pipeline (Offline)
Historical user features are loaded from Parquet files. The ML model is trained, registered in **MLflow**, and its artifacts are saved to **MinIO**. **Feast** materializes these baseline features into **Redis**.

### 2️⃣ The Streaming Pipeline (Online)
1. **Producer** (`event_simulator`): Synthetic live user interactions are published to the Redpanda Kafka broker.
2. **Consumer** (`stream_processor`): Apache Spark catches events instantly, recalculating moving averages across distributed nodes on the fly.
3. **PushSource**: Fresh calculations are injected directly into the Redis Online Store using Feast's streaming trapdoor, instantly overriding batch data.

### 3️⃣ Real-Time Inference
When a request hits the FastAPI `/predict` endpoint, it pulls the absolute freshest data from Redis. The prediction shifts dynamically as live events occur.

---

## 📊 Observability & SRE (New in v3.0)

StreamRec 3.0 exposes internal FastAPI metrics via `prometheus-fastapi-instrumentator`. Prometheus scrapes these metrics every 5 seconds, and Grafana visualizes the industry-standard **Four Golden Signals**:

- **Traffic**: Total requests per second.

- **Latency**: P95 response times (sub-100ms inference).

- **Errors**: HTTP 4xx and 5xx exception tracking.

- **Status Codes**: Traffic distribution visualization.

---

## 📂 Project Structure

```text
stream-rec/
├── .github/workflows/       # CI/CD Automation (GitHub Actions)
├── dashboards/              # Dashboards as Code (Grafana JSON exports)
├── feature_repo/            # Feast Feature Store Definitions & Data
├── prometheus/              # Metrics scraping configuration
├── services/                # Containerized Microservices
│   ├── event_simulator/     # Generates live Kafka traffic
│   ├── inference_api/       # FastAPI Prediction Server
│   └── stream_processor/    # PySpark Streaming consumer
├── training/                # Offline Batch Training (MLflow + MinIO)
├── docker-compose.yml       # Infrastructure orchestration
└── Makefile                 # One-click CLI orchestration
```
---

## 🚀 Quick Start

### 1️⃣ Spin Up the Infrastructure

Clone the repository and spin up the core data infrastructure (Postgres, MinIO, Redis, Redpanda, Prometheus, Grafana).

```Bash
git clone https://github.com/sythe95/stream-rec.git
cd stream-rec
make up
```

(Wait ~30 seconds for containers to initialize).

---

### 2️⃣ Train the Model & Materialize Baseline
```Bash
make train
```
This extracts offline features, trains the model, logs it to MLflow, and materializes the baseline features into Redis.

### 3️⃣ Start the Real-Time Loop
Open multiple terminal windows to watch the system react live:

**Terminal A** (Start generating live traffic):

```Bash
make producer
```
**Terminal B** (Start the Spark Stream Processor):

```Bash
make consumer
```

### 4️⃣ Test the Inference & Spike the Dashboard
To see the real-time inference in action and spike your Grafana dashboards, run this infinite load-testing loop:

```Bash
while true; do
    curl -s -X POST "http://localhost:8000/predict" \
         -H "Content-Type: application/json" \
         -d '{"user_id": 1}' > /dev/null
done
```
(Press `Ctrl+C` to stop the attack).

### 5️⃣ Tear Down
```Bash
make down
```
(Note: Grafana dashboards are saved to a persistent Docker volume and will survive teardowns).

---

## 🌐 Web Interfaces
- **Grafana SRE Dashboards**: http://localhost:3000 (User/Pass: admin/admin)

- **Prometheus Metrics**: http://localhost:9090

- **MLflow Model Registry**: http://localhost:5000

- **MinIO S3 Buckets**: http://localhost:9001

- **FastAPI Swagger Docs**: http://localhost:8000/docs