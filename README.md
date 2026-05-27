# Нефтегаз — корпоративный портал нефтепромышленной компании

Проект итоговой аттестации по дисциплине **«Проектный практикум»** (6 семестр).
Веб-приложение для учёта месторождений, скважин и заявок на обслуживание.

## Описание проекта

Корпоративный портал для сотрудников нефтепромышленной компании. Позволяет
вести каталог месторождений и скважин, отслеживать их статус, создавать заявки
на ремонт и плановое ТО, разграничивать доступ по ролям (`employee`, `admin`).

## Основные возможности

- Регистрация и вход пользователей (JWT-аутентификация)
- Каталог месторождений: поиск, фильтрация по статусу, создание / редактирование / удаление (для администратора)
- Карточка месторождения с привязанными скважинами и сводкой по добыче
- Каталог скважин с фильтрацией по статусу и привязкой к месторождению
- Заявки на обслуживание: создание сотрудником, смена статуса и приоритета
- Swagger-документация API по адресу `/docs`
- Покрытие тестами ключевых сценариев (auth, fields, wells) с отдельной тестовой БД

## Стек технологий

| Слой       | Технологии                                              |
|------------|---------------------------------------------------------|
| Backend    | Python 3.11, FastAPI, SQLAlchemy 2, Pydantic 2, Alembic |
| Auth       | JWT (python-jose), bcrypt (passlib)                     |
| База данных| PostgreSQL 15                                           |
| Frontend   | React 18, Vite 5, React Router 6                        |
| Тесты      | pytest, httpx (TestClient)                              |
| Инфра      | Docker Compose (postgres + test-postgres)               |

## Структура проекта

```
maxi-practic/
├── backend/
│   ├── app/
│   │   ├── main.py            # точка входа FastAPI
│   │   ├── config.py          # настройки (Pydantic Settings)
│   │   ├── database.py        # подключение и сессии SQLAlchemy
│   │   ├── models.py          # ORM-модели User, OilField, Well, MaintenanceRequest
│   │   ├── schemas.py         # Pydantic-схемы запросов/ответов
│   │   ├── auth.py            # хеширование паролей и JWT
│   │   ├── deps.py            # зависимости (current_user, require_admin)
│   │   └── routers/           # auth.py, fields.py, wells.py, requests.py
│   ├── alembic/               # миграции (env.py, versions/0001_initial.py)
│   ├── tests/                 # conftest + test_auth/test_fields/test_wells
│   ├── scripts/seed.py        # демо-данные
│   ├── requirements.txt
│   ├── alembic.ini
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.jsx / App.jsx
│   │   ├── api.js             # HTTP-клиент к backend
│   │   ├── auth.jsx           # AuthContext + useAuth()
│   │   ├── components/        # Navbar, Layout, ProtectedRoute
│   │   └── pages/             # Home, Login, Register, Fields, FieldDetail, Wells, Requests
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
├── docs/
│   ├── user_stories.md        # роли и пользовательские истории
│   ├── models.md              # описание сущностей и связей
│   └── presentation.md        # текст-сценарий защиты
├── docker-compose.yml         # postgres (prod) и postgres (test)
└── README.md
```

## Переменные окружения проекта

### Backend (`backend/.env`)

| Переменная                    | Назначение                                      | Пример                                                                       |
|-------------------------------|-------------------------------------------------|------------------------------------------------------------------------------|
| `DATABASE_URL`                | Строка подключения к основной БД                | `postgresql+psycopg://neftegaz:neftegaz@localhost:5432/neftegaz`             |
| `TEST_DATABASE_URL`           | Строка подключения к тестовой БД                | `postgresql+psycopg://neftegaz:neftegaz@localhost:5433/neftegaz_test`        |
| `SECRET_KEY`                  | Секрет для подписи JWT                          | `change_me_to_long_random_string`                                            |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни access-токена в минутах             | `60`                                                                         |
| `CORS_ORIGINS`                | Список разрешённых origin'ов через запятую      | `http://localhost:5173`                                                      |

### Frontend (`frontend/.env`)

| Переменная       | Назначение                          | Пример    |
|------------------|-------------------------------------|-----------|
| `VITE_API_BASE`  | Базовый URL API (через vite-proxy)  | `/api`    |

## Как запустить проект

### 1. База данных

```bash
docker compose up -d db db_test
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate            # Linux/macOS
# .venv\Scripts\activate             # Windows
pip install -r requirements.txt
cp .env.example .env

alembic upgrade head                  # накатить миграции
python -m scripts.seed                # (опционально) заполнить демо-данными

uvicorn app.main:app --reload --port 8000
```

API будет доступен на `http://localhost:8000`, Swagger — на `http://localhost:8000/docs`.

### 3. Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Сайт откроется на `http://localhost:5173`.

### 4. Тесты

```bash
cd backend
TEST_DATABASE_URL=postgresql+psycopg://neftegaz:neftegaz@localhost:5433/neftegaz_test pytest
```

### Тестовые учётные записи (после seed)

| Роль       | Email                 | Пароль     |
|------------|-----------------------|------------|
| Админ      | `admin@neftegaz.ru`   | `admin123` |
| Сотрудник  | `user@neftegaz.ru`    | `user1234` |

## Команда проекта

- Мамонов Александр — Lead
- Кузьма Кузнецов — DB dev
- Дмитрий Шинкаренко — Document lead
- Егор Андреев — Backend dev
- Доменик Каличава — Frontend dev
- Никита Лукашев — DevOps
- Кирилл Щерба — QA Engineer

## Лицензия

Учебный проект, для свободного использования в рамках курса.
