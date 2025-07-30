from sqlalchemy.orm import declarative_base

from thalentfrx.configs.Database import Engine

# Base Entity Model Schema
EntityMeta = declarative_base()


def init():
    EntityMeta.metadata.create_all(bind=Engine)
