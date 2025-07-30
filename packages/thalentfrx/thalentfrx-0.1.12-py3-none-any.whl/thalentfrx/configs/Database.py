from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from thalentfrx.configs.Environment import get_environment_variables

# Runtime Environment Configuration
env = get_environment_variables()

# Generate Database URL
if env.DATABASE_SSL_MODE:
    DATABASE_URL = (f"{env.DATABASE_DIALECT}://{env.DATABASE_USERNAME}:{env.DATABASE_PASSWORD}"
                    f"@{env.DATABASE_HOSTNAME}:{env.DATABASE_PORT}/{env.DATABASE_NAME}?sslmode=require")
else:
    DATABASE_URL = (f"{env.DATABASE_DIALECT}://{env.DATABASE_USERNAME}:{env.DATABASE_PASSWORD}"
                    f"@{env.DATABASE_HOSTNAME}:{env.DATABASE_PORT}/{env.DATABASE_NAME}")

# Create Database Engine
Engine = create_engine(
    DATABASE_URL, echo=env.DEBUG_MODE, future=True
)


# Create Database Engine
@lru_cache(maxsize=None)
def get_engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True, echo=env.DEBUG_MODE, future=True)


SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=Engine
)


def get_db_connection():
    db = scoped_session(SessionLocal)
    try:
        yield db
    finally:
        db.close()
