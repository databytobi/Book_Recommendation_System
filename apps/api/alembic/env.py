# Create updated env.py for Docker

# alembic/env.py

import sys
import os
from pathlib import Path
from logging.config import fileConfig

# pyrefly: ignore [missing-import]
from sqlalchemy import engine_from_config

# pyrefly: ignore [missing-import]
from sqlalchemy import pool

from alembic import context

# For Docker container - app is directly in /app
# Get the directory where this file is located
current_dir = Path(__file__).parent
project_root = current_dir.parent

# Add the project root to sys.path
sys.path.insert(0, str(project_root))

print(f"Project root: {project_root}")

try:
    from app.core.database import Base
    from app.core.config import settings

    print("Successfully imported app modules!")
except ImportError as e:
    print(f"Import error: {e}")
    raise

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URL from your settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Add your model's MetaData object here
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
