from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy import create_engine
from alembic import context
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Event_Pulse_app.db_base import Base
from Event_Pulse_app import models

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

from dotenv import load_dotenv
import os

def get_url():
    """🌟 Динамическая сборка URL из .env без хардкода"""
    # Загружаем переменные из файла .env, который лежит на шаг выше папки alembic
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
    load_dotenv(dotenv_path)

    # Читаем чистые параметры из вашего .env
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")
    db_name = os.getenv("DB_NAME", "event_pulse_database")
    port = os.getenv("DB_PORT", "5432")
    
    # 🌟 Главная магия автоматизации:
    # Если мы внутри Docker-контейнера, системный хост ВСЕГДА равен 'db'.
    # Если мы запускаем код локально на ПК, хост будет равен значению из .env (localhost).
    if os.path.exists("/.dockerenv"):
        host = "db"
    else:
        host = os.getenv("DB_HOST", "localhost")

    # Собираем чистую синхронную строку для Alembic
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def run_migrations_offline():
    url = get_url() # Используем наш умный метод получения URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    # Передаем динамический URL вместо жесткого из alembic.ini
    connectable = create_engine(
        get_url(),
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
