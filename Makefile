include .env
export

.PHONY: run prod test

run:
	@uv run fastapi dev ./src/app/main.py

prod:
	@uv run uvicorn app.main:app --reload --reload-exclude "*.db" --reload-exclude "*.csv"

up:
	@docker-compose up -d --build

down:
	@docker compose down -v --rmi local

test:
	@uv run pytest -v