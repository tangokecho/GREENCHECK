SHELL := /bin/sh

.PHONY: env.init dev up demo

# 1) Create .env from example
env.init:
	@if [ -f .env ]; then \
		echo ".env already exists"; \
	else \
		cp .env.example .env && echo ".env created from .env.example"; \
	fi

# 2) Boot everything (first run builds images)
dev:
	docker compose up --build

# Detached
up:
	docker compose up -d --build

# 3) Generate a demo bundle (ZIP appears at ./dist/demo_packet.zip)
demo:
	python3 scripts/build_demo_bundle.py
