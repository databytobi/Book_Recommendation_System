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

# Get the project root (where alembic.ini is located)
project_root = Path(__file__).parent.parent

# Your app is located at: apps/api/app/
app_path = project_root / "apps" / "api" / "app"

# Add the parent directory of 'app' to sys.path
# So that 'app' becomes importable
sys.path.insert(0, str(app_path.parent))

print(f"Project root: {project_root}")
print(f"App path added to sys.path: {app_path.parent}")
print(f"Does app exist? {(app_path).exists()}")

try:
    # Now you can import from app
    # pyrefly: ignore [missing-import]
    from app.core.database import Base
    # pyrefly: ignore [missing-import]
    from app.core.config import settings
    print("Successfully imported app modules!")
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Contents of {app_path.parent}: {list(app_path.parent.iterdir())}")
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
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()