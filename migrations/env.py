from logging.config import fileConfig
from alembic import context
from database.database import Base
import database.models  

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

db_url = "postgresql://"
config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        transaction_per_migration=True,
    )
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
