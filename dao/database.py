from pathlib import Path
from urllib.parse import quote_plus

import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def _load_database_config() -> dict:
    config_path = Path(__file__).resolve().parent.parent / "config.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    database_config = config.get("DATABASE", {})

    required_keys = ("HOST", "PORT", "NAME", "USER", "PASSWORD")
    missing_keys = [key for key in required_keys if key not in database_config]
    if missing_keys:
        missing_config = ", DATABASE.".join(missing_keys)
        raise ValueError(f"Missing database config: DATABASE.{missing_config}")

    return database_config


database_config = _load_database_config()
DB_HOST = database_config["HOST"]
DB_PORT = database_config["PORT"]
DB_NAME = database_config["NAME"]
DB_USER = database_config["USER"]
DB_PASSWORD = database_config["PASSWORD"]

DATABASE_URL = (
    f"postgresql+psycopg2://{quote_plus(str(DB_USER))}:{quote_plus(str(DB_PASSWORD))}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
