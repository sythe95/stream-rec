# 🚀 StreamRec 2.0 Quick Commands

# Define the container engine so it works natively without relying on aliases
ENGINE ?= podman
COMPOSE ?= podman-compose

.PHONY: up down train producer consumer sync restart

# Bring up the whole infrastructure
up:
	$(COMPOSE) --env-file .env up -d

# Tear down the infrastructure
down:
	$(COMPOSE) down

# Run the Feast feature extraction and MLflow training script
train:
	$(ENGINE) exec stream_rec_api python train_model.py

# Start generating fake live user traffic
producer:
	python3 src/producer.py

# Start the stream processor to catch ratings
consumer:
	$(ENGINE) exec -it stream_rec_api python -u consumer.py

# Quickly sync your local Windows scripts into the running container
sync:
	$(ENGINE) cp src/predict_model.py stream_rec_api:/app/predict_model.py
	$(ENGINE) cp src/consumer.py stream_rec_api:/app/consumer.py

# Force restart the API container to clear memory and load new code
restart:
	$(ENGINE) restart stream_rec_api