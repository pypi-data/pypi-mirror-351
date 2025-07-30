import contextlib
from typing import Any, Dict, Iterator

from sqlalchemy import create_engine, Connection
from sqlalchemy.orm import scoped_session, sessionmaker, Session

from thalentfrx.configs.Environment import get_environment_variables

# Runtime Environment Configuration
env = get_environment_variables()

# Generate Database URL
DATABASE_URL = f"{env.DATABASE_DIALECT}://{env.DATABASE_USERNAME}:{env.DATABASE_PASSWORD}@{env.DATABASE_HOSTNAME}:{env.DATABASE_PORT}/{env.DATABASE_NAME}"

class SessionManager:
    def __init__(self, host: str, engine_kwargs: Dict[str, Any] = {}):
        self._engine = create_engine(host, **engine_kwargs)
        self._sessionmaker = sessionmaker(autocommit=False, bind=self._engine)

    def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.contextmanager
    def connect(self) -> Iterator[Connection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                connection.rollback()
                raise

    @contextlib.contextmanager
    def session(self) -> Iterator[Session]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


sessionmanager = SessionManager(DATABASE_URL, {"echo": env.DEBUG_MODE, "pool_pre_ping": True})


def get_db_session():
    with sessionmanager.session() as session:
        yield session
        
def get_scoped_db_session():
    with sessionmanager.session() as session:
        yield scoped_session(session)