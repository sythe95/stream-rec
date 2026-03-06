# 🚀 StreamRec 2.0
**End-to-End Real-Time MLOps & Streaming Platform**

[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Apache Kafka](https://img.shields.io/badge/Kafka-(Redpanda)-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)](https://redpanda.com/)
[![Feast](https://img.shields.io/badge/Feast-Feature_Store-orange?style=for-the-badge)](https://feast.dev/)
[![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white)](https://mlflow.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)

---

**StreamRec 2.0** is a fully containerized, production-grade **real-time MLOps platform** utilizing a Lambda architecture to deliver **low-latency inference at scale**.

While this repository demonstrates a **Recommendation System**, this exact architectural pattern is used in production for:
- Fraud Detection (catching anomalies in milliseconds)
- Dynamic Pricing (Uber surge pricing logic)
- Real-Time Churn Prediction
- Any ML workload requiring live, stateful context.

The core philosophy of StreamRec:
> **Train on history. React in real-time. Never drift.**

By combining **Redpanda (Kafka)** for event streaming, **Feast** (via PushSource) for sub-millisecond feature injection, and **MLflow** for model lifecycle management, StreamRec completely eliminates training-serving skew.

---

## 🏗️ System Architecture

StreamRec runs a decoupled microservice stack orchestrated via Docker/Podman Compose.


| Component | Technology | Role |
|-----------|------------|------|
| **Message Broker** | Redpanda (Kafka) | High-throughput, low-latency event streaming |
| **Stream Processor** | Python (KafkaConsumer) | Calculates rolling ML features in real-time |
| **Feature Store** | Feast + Redis | Low-latency feature serving via PushSource |
| **Model Registry** | MLflow + Postgres | Tracks models, metrics, and versions |
| **Artifact Store** | MinIO (S3) | Stores serialized model artifacts |
| **Prediction API** | FastAPI | Serves dynamic, real-time inferences |

---

## 🌊 Data Flow (The Lambda Architecture)

### 1️⃣ The Batch Pipeline (Offline)
Historical user features are loaded from Parquet files. The ML model is trained, registered in **MLflow**, and its artifacts are saved to **MinIO**. **Feast** materializes these baseline features into **Redis**.

### 2️⃣ The Streaming Pipeline (Online)
1. **Producer:** Synthetic live user interactions (e.g., ratings) are published to the Redpanda Kafka broker.
2. **Consumer:** A stream processor catches events instantly, recalculating moving averages on the fly.
3. **PushSource:** Fresh calculations are forcefully injected directly into the Redis Online Store using Feast's streaming trapdoor, instantly overriding batch data.

### 3️⃣ Real-Time Inference
When a request hits the FastAPI `/predict` endpoint, it pulls the absolute freshest data from Redis. The prediction shifts dynamically as live events occur.

---

## 📂 Project Structure

```text
stream-rec/
├── src/
│   ├── producer.py          # Generates live Kafka traffic
│   ├── consumer.py          # Stream processor & Feast PushSource injector
│   ├── train_model.py       # Pipeline: Fetch -> Train -> MLflow
│   ├── predict_model.py     # FastAPI Server
│   └── ...
├── feature_repo/            # Feast Feature Store Definitions
│   ├── feature_store.yaml   # Connection config
│   ├── definitions.py       # Batch sources, Views, and PushSource trapdoor
│   └── data/                # Offline Parquet files
├── docker-compose.yml       # Infrastructure orchestration
├── Makefile                 # 🚀 One-click CLI orchestration
└── README.md
```
---

## 🚀 Quick Start

### 1️⃣ Prerequisites

Make sure the following tools are installed on your system:

- **Docker Desktop** or **Podman** (must be running)
- **Git**
- **Make** (via WSL or Linux)

---

### 2️⃣ Spin Up the Infrastructure

We use a **Makefile** to simplify orchestration.

Run the following commands in your terminal:

```bash
git clone https://github.com/sythe95/stream-rec.git
cd stream-rec
make up
```
(Wait ~30 seconds for Postgres, MinIO, Redis, and Redpanda to initialize).

### 3️⃣ Train the Model & Materialize Baseline
```Bash
make train
```
This extracts offline features, trains the Scikit-Learn model, logs it to MLflow, and materializes the baseline features into Redis.

### 4️⃣ Start the Real-Time Loop
You will need multiple terminal windows to watch the system react live:

**Terminal A** (Start generating live traffic):

```Bash
make producer
```
**Terminal B** (Start the Stream Processor):

```Bash
make consumer
```
Watch as it catches live events, calculates new averages, and pushes them instantly into Redis.

**Terminal C** (Watch the ML Model react):

Ping the inference API to see predictions change dynamically based on the live data stream:

```Bash
while true; do
    curl -s -X POST "http://localhost:8000/predict" \
         -H "Content-Type: application/json" \
         -d '{"user_id": 1}'
    echo -e "\n-----------------------------------"
    sleep 2
done
```
### 5️⃣ Tear Down
```Bash
make down
```
## 🌐 Web Interfaces
MLflow Model Registry: http://localhost:5000

MinIO S3 Buckets: http://localhost:9001

FastAPI Swagger Docs: http://localhost:8000/docs