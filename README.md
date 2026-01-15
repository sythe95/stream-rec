# 🎬 StreamRec: Real-Time Recommendation MLOps Pipeline

**StreamRec** is an end-to-end MLOps platform capable of serving real-time recommendations. It demonstrates a complete production lifecycle: from feature engineering to model deployment using Docker, Feast, MLflow, and FastAPI.

## 🏗️ Architecture

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Feature Store** | [Feast](https://feast.dev/) + [Redis](https://redis.io/) | Low-latency feature serving for real-time inference. |
| **Model Registry** | [MLflow](https://mlflow.org/) + [Postgres](https://www.postgresql.org/) | Tracking experiments, parameters, and model artifacts. |
| **Object Storage** | [MinIO](https://min.io/) | S3-compatible storage for model binaries. |
| **Serving API** | [FastAPI](https://fastapi.tiangolo.com/) | REST API for generating predictions. |
| **Containerization**| [Docker](https://www.docker.com/) | Unified environment for reproducibility. |

## 🚀 Getting Started

### 1. Prerequisites
* Docker & Docker Compose
* Python 3.10+

### 2. Launch the Stack
```bash
docker compose up -d --build