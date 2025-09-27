import os
import sys
import importlib
import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

@pytest.fixture(scope="session")
def app():
    mod = importlib.import_module("main")
    return mod.app

@pytest.fixture()
def client(app):
    return TestClient(app)
