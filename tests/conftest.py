import os
import sys
from pathlib import Path

import pytest
from flask import Flask

os.environ.setdefault("CLASH_DEV_PREFLIGHT", "False")
os.environ.setdefault("CLASH_INIT_DB_ON_START", "False")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_PARENT = PROJECT_ROOT.parent
if str(PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(PROJECT_PARENT))


@pytest.fixture
def app() -> Flask:
    from ClashRecruit.app import app as clash_app

    clash_app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
    )
    return clash_app


@pytest.fixture
def client(app: Flask):
    return app.test_client()


@pytest.fixture(autouse=True)
def reset_rate_limits():
    from ClashRecruit.services.rate_limiter import reset_rate_limits

    reset_rate_limits()


@pytest.fixture
def set_session(client):
    def _set_session(**values):
        with client.session_transaction() as sess:
            sess.update(values)

    return _set_session
