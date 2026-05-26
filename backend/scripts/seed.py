"""Заполняет БД демо-данными: админ + пара месторождений со скважинами."""
from datetime import datetime

from app.auth import hash_password
from app.database import SessionLocal
from app.models import (
    FieldStatus,
    OilField,
    User,
    UserRole,
    Well,
    WellStatus,
)


def run() -> None:
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "admin@neftegaz.ru").first():
            db.add(
                User(
                    email="admin@neftegaz.ru",
                    full_name="Главный администратор",
                    password_hash=hash_password("admin123"),
                    role=UserRole.admin,
                )
            )
        if not db.query(User).filter(User.email == "user@neftegaz.ru").first():
            db.add(
                User(
                    email="user@neftegaz.ru",
                    full_name="Иван Сотрудник",
                    password_hash=hash_password("user1234"),
                    role=UserRole.employee,
                )
            )

        if not db.query(OilField).first():
            samotlor = OilField(
                name="Самотлорское",
                location="ХМАО, Нижневартовск",
                reserves_tons=1_200_000.0,
                discovered_year=1965,
                status=FieldStatus.active,
                description="Крупнейшее нефтяное месторождение России.",
            )
            priob = OilField(
                name="Приобское",
                location="ХМАО, Ханты-Мансийск",
                reserves_tons=900_000.0,
                discovered_year=1982,
                status=FieldStatus.active,
                description="Одно из крупнейших разрабатываемых месторождений.",
            )
            db.add_all([samotlor, priob])
            db.flush()

            db.add_all([
                Well(
                    field_id=samotlor.id,
                    name="СКВ-101",
                    depth_m=2450.0,
                    daily_output_tons=180.0,
                    status=WellStatus.operating,
                    drilled_at=datetime(2018, 6, 1),
                ),
                Well(
                    field_id=samotlor.id,
                    name="СКВ-102",
                    depth_m=2600.0,
                    daily_output_tons=0,
                    status=WellStatus.maintenance,
                    drilled_at=datetime(2019, 3, 12),
                ),
                Well(
                    field_id=priob.id,
                    name="ПРБ-7",
                    depth_m=2700.0,
                    daily_output_tons=150.0,
                    status=WellStatus.operating,
                    drilled_at=datetime(2020, 9, 9),
                ),
            ])

        db.commit()
        print("Демо-данные загружены")
    finally:
        db.close()


if __name__ == "__main__":
    run()
