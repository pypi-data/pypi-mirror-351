from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


def create_pg_database_session(
    user: str, password: str, host: str, database: str, port: int = 5432
) -> Session:
    database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"

    engine = create_engine(database_url, pool_pre_ping=True)

    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return session()
