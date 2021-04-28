from __future__ import with_statement
import os
import sys
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
root = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                    os.path.pardir,
                    os.path.pardir,
                    os.path.pardir)  # 定位到项目根目录
sys.path.append(root)
from myapp.models import metadata
from myapp.conf.config import settings
url = settings.db.pymysql_url  # 数据库alembic管理依然使用pymysql; 业务查询使用aiomysql
# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # connectable = engine_from_config(
    #     config.get_section(config.config_ini_section),
    #     prefix='sqlalchemy.',
    #     poolclass=pool.NullPool)
    connectable = engine_from_config(
        {"sqlalchemy.url": url},  # 使用dynaconf文件的配置替换alembic.ini的配置
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
