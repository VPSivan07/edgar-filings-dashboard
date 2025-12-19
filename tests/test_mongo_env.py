import pytest
from pathlib import Path
from importlib import util
import types
import sys


def _load_mongo_module():
    # Ensure a dummy `pymongo` is available so tests don't require an actual pymongo install
    if "pymongo" not in sys.modules:
        fake = types.ModuleType("pymongo")
        # provide a placeholder MongoClient to satisfy imports; tests will monkeypatch it when needed
        class _PlaceholderClient:
            def __init__(self, *args, **kwargs):
                class Admin:  # minimal admin that does nothing unless replaced
                    def command(self, cmd):
                        return None
                self.admin = Admin()

        fake.MongoClient = _PlaceholderClient
        sys.modules["pymongo"] = fake

    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / "streamlit_app" / "mongo.py"
    spec = util.spec_from_file_location("streamlit_app.mongo", str(module_path))
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_missing_mongo_uri(tmp_path):
    # no MONGO_URI present
    env_file = tmp_path / ".env"
    env_file.write_text("")

    mod = _load_mongo_module()

    with pytest.raises(RuntimeError, match="Missing `MONGO_URI`"):
        mod.get_mongo_client_from_env(str(env_file))


def test_unable_to_connect(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text('MONGO_URI="mongodb://bad:27017"\nMONGO_DB="edgar"')

    # monkeypatch MongoClient on the dynamically loaded module so we don't perform a real network call
    class DummyAdmin:
        def command(self, cmd):
            raise Exception("connection refused")

    class DummyClient:
        def __init__(self, *args, **kwargs):
            self.admin = DummyAdmin()

    mod = _load_mongo_module()
    monkeypatch.setattr(mod, "MongoClient", DummyClient)

    with pytest.raises(RuntimeError, match="Unable to connect to MongoDB"):
        mod.get_mongo_client_from_env(str(env_file))
