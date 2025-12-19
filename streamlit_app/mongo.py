from __future__ import annotations

from dotenv import dotenv_values
from pymongo import MongoClient
import certifi


def get_mongo_client_from_env(env_path: str = ".env"):
    """Return a (MongoClient, db_name) tuple or raise RuntimeError on failure.

    This function reads the `.env` file at `env_path` (using python-dotenv's
    `dotenv_values`), enforces that `MONGO_URI` is present, and attempts a
    `ping` to fail fast on unreachable servers.
    """
    _env = dotenv_values(env_path)
    MONGO_URI = _env.get("MONGO_URI")
    MONGO_DB = _env.get("MONGO_DB") or "edgar"

    if not MONGO_URI:
        raise RuntimeError("Missing `MONGO_URI` in `.env`.")

    try:
        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=30000,
            socketTimeoutMS=30000,
            connectTimeoutMS=30000,
        )
        # fail fast
        client.admin.command("ping")
    except Exception as exc:  # pragma: no cover - runtime failure handling
        raise RuntimeError(f"Unable to connect to MongoDB: {exc}") from exc

    return client, MONGO_DB
