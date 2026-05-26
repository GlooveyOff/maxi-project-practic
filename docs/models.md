# Модели данных

## Сущности

### User — пользователь системы

| Поле           | Тип            | Ограничения                                  |
|----------------|----------------|----------------------------------------------|
| id             | int            | PK                                           |
| email          | str(255)       | unique, not null, валидный email             |
| full_name      | str(150)       | not null, 2…150 символов                     |
| password_hash  | str(255)       | хеш bcrypt, в API не возвращается            |
| role           | enum UserRole  | `guest` / `employee` / `admin`, default `employee` |
| is_active      | bool           | default `true`                               |
| created_at     | datetime       | server default `now()`                       |

### OilField — месторождение

| Поле             | Тип               | Ограничения                                                   |
|------------------|-------------------|---------------------------------------------------------------|
| id               | int               | PK                                                            |
| name             | str(150)          | unique, not null                                              |
| location         | str(200)          | not null                                                      |
| reserves_tons    | float             | ≥ 0                                                           |
| discovered_year  | int               | 1900 … 2100                                                   |
| status           | enum FieldStatus  | `exploration` / `active` / `suspended` / `depleted`           |
| description      | text              | nullable                                                      |
| created_at       | datetime          | server default `now()`                                        |

### Well — скважина

| Поле              | Тип              | Ограничения                                          |
|-------------------|------------------|------------------------------------------------------|
| id                | int              | PK                                                   |
| field_id          | int              | FK → `fields.id`, on delete CASCADE                  |
| name              | str(100)         | not null                                             |
| depth_m           | float            | > 0                                                  |
| daily_output_tons | float            | ≥ 0, default 0                                       |
| status            | enum WellStatus  | `drilling` / `operating` / `maintenance` / `closed`  |
| drilled_at        | datetime         | nullable                                             |
| created_at        | datetime         | server default `now()`                               |

### MaintenanceRequest — заявка на обслуживание

| Поле        | Тип                  | Ограничения                                          |
|-------------|----------------------|------------------------------------------------------|
| id          | int                  | PK                                                   |
| well_id     | int                  | FK → `wells.id`, on delete CASCADE                   |
| author_id   | int                  | FK → `users.id`, on delete SET NULL                  |
| title       | str(200)             | 3…200 символов                                       |
| description | text                 | not null                                             |
| status      | enum RequestStatus   | `new` / `in_progress` / `done` / `rejected`          |
| priority    | enum RequestPriority | `low` / `medium` / `high` / `critical`               |
| created_at  | datetime             | server default `now()`                               |

## Связи

```
User 1 ──< MaintenanceRequest >── 1 Well >── 1 OilField
```

- Одно **месторождение** содержит много **скважин** (1:N, on delete CASCADE).
- Одна **скважина** имеет много **заявок** (1:N, on delete CASCADE).
- Один **пользователь** может быть автором многих **заявок** (1:N, on delete SET NULL).

## Валидация на уровне API (Pydantic)

- `email` проверяется `EmailStr`.
- `password` ≥ 6 символов.
- `reserves_tons`, `depth_m`, `daily_output_tons` — числа с ограничениями
  (`ge=0` / `gt=0`).
- `discovered_year` — 1900…2100.
- При создании скважины проверяется, что указанное месторождение существует.
- При создании заявки проверяется существование скважины.
