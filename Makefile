.PHONY: all setup test lint format typecheck migrate up down seed

up:
	docker compose up -d --build

down:
	docker compose down -v

test:
	docker compose exec api pytest tests/unit tests/api tests/integration

test-all:
	docker compose exec api pytest tests

lint:
	docker compose exec api ruff check .

format:
	docker compose exec api ruff format .

typecheck:
	docker compose exec api mypy app

migrate:
	docker compose exec api alembic upgrade head

seed:
	docker compose exec api python -m scripts.seed

frontend-checks:
	cd frontend && npm run typecheck && npm run lint && npm run test
