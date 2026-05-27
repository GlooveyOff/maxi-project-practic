.PHONY: help db db-down migrate seed back front test fmt build up down logs

help:
	@echo "Доступные команды:"
	@echo "  make db        — поднять PostgreSQL (prod + test) в docker"
	@echo "  make db-down   — остановить контейнеры postgres"
	@echo "  make migrate   — накатить миграции Alembic"
	@echo "  make seed      — загрузить демо-данные"
	@echo "  make back      — запустить uvicorn (бэкенд) на 8000"
	@echo "  make front     — запустить vite dev server (фронт) на 5173"
	@echo "  make test      — прогнать pytest"
	@echo "  make build     — собрать docker-образы backend и frontend"
	@echo "  make up        — поднять весь стек в docker (профиль full)"
	@echo "  make down      — погасить весь стек"
	@echo "  make logs      — логи сервиса api"

db:
	docker compose up -d db db_test

db-down:
	docker compose stop db db_test

migrate:
	cd backend && .venv/bin/alembic upgrade head

seed:
	cd backend && .venv/bin/python -m scripts.seed

back:
	cd backend && .venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

front:
	cd frontend && npm run dev

test:
	cd backend && TEST_DATABASE_URL=postgresql+psycopg://neftegaz:neftegaz@localhost:5433/neftegaz_test .venv/bin/pytest

build:
	docker compose --profile full build

up:
	docker compose --profile full up -d

down:
	docker compose --profile full down

logs:
	docker compose logs -f api
