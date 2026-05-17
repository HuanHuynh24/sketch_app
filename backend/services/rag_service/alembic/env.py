from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, text

from alembic import context

from app.core.config import settings
from app.models.base import Base

# Import models của service tại đây sau khi tạo model.
import app.models
# Ví dụ:
# from app.models.user import User
# from app.models.question import Question


config = context.config

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table":
        return object.schema == settings.DB_SCHEMA
    return True


def run_migrations_offline():
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        version_table=f"alembic_version_{settings.DB_SCHEMA}",
        version_table_schema=settings.DB_SCHEMA,
        include_object=include_object,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        connection.execute(
            text(f'CREATE SCHEMA IF NOT EXISTS "{settings.DB_SCHEMA}"')
        )
        connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table=f"alembic_version_{settings.DB_SCHEMA}",
            version_table_schema=settings.DB_SCHEMA,
            include_object=include_object,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()