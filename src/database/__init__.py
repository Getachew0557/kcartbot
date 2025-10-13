from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_URL


def _build_engine():
	url = (DATABASE_URL or "").strip()
	if not url or "://" not in url:
		raise RuntimeError(
			f"Invalid DATABASE_URL: '{url}'. Expected format: dialect+driver://user:password@host:port/dbname"
		)
	# SQLite needs a special connect arg; others can use defaults
	if url.startswith("sqlite"):
		return create_engine(url, connect_args={"check_same_thread": False}, pool_pre_ping=True)
	return create_engine(url, pool_pre_ping=True)


engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

__all__ = ["engine", "SessionLocal"]
