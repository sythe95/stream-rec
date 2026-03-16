# 🚀 StreamRec 3.0 CLI

ENGINE ?= docker
COMPOSE ?= docker compose

.PHONY: up down train logs restart

up:
	$(COMPOSE) --env-file .env up -d --build

down:
	$(COMPOSE) down -v

train:
	$(ENGINE) exec -it stream_rec_inference_api bash -c "cd feature_repo && feast apply && cd .. && python -u training/train.py"

logs:
	$(COMPOSE) logs -f stream_processor event_simulator inference_api

restart:
	$(ENGINE) restart stream_rec_inference_api