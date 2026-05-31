"""Regression tests for import-time backend side effects."""

import importlib
import os
import sys
import unittest
from unittest.mock import patch

MODULES_TO_IMPORT = [
    "ClashRecruit.app",
    "ClashRecruit.routes.home_route",
    "ClashRecruit.routes.session_state_route",
    "ClashRecruit.routes.recruiter_route",
    "ClashRecruit.routes.recruitee_route",
    "ClashRecruit.routes.locations_route",
    "ClashRecruit.routes.saved_clans_route",
    "ClashRecruit.routes.imported_clans_route",
    "ClashRecruit.services.import_clash_api_clans",
    "ClashRecruit.services.refresh_db",
]


class ImportSideEffectsTests(unittest.TestCase):
    def _clear_repo_modules(self):
        for module_name in list(sys.modules):
            if module_name == "ClashRecruit" or module_name.startswith(
                "ClashRecruit."
            ):
                sys.modules.pop(module_name, None)

    def test_importing_backend_modules_does_not_create_mongo_client(self):
        self._clear_repo_modules()

        with patch.dict(
            os.environ,
            {
                "DBURI": "",
                "CLASH_INIT_DB_ON_START": "False",
                "CLASH_DEV_PREFLIGHT": "False",
            },
            clear=False,
        ):
            with patch("pymongo.mongo_client.MongoClient") as mock_client:
                for module_name in MODULES_TO_IMPORT:
                    importlib.import_module(module_name)

        self.assertFalse(mock_client.called)

    def test_backend_modules_import_cleanly_without_runtime_side_effects(self):
        self._clear_repo_modules()

        with patch.dict(
            os.environ,
            {
                "DBURI": "",
                "CLASH_INIT_DB_ON_START": "False",
                "CLASH_DEV_PREFLIGHT": "False",
            },
            clear=False,
        ):
            for module_name in MODULES_TO_IMPORT:
                with self.subTest(module=module_name):
                    importlib.import_module(module_name)

    def test_app_import_runs_preflight_when_enabled(self):
        self._clear_repo_modules()

        with patch.dict(
            os.environ,
            {
                "DBURI": "",
                "CLASH_INIT_DB_ON_START": "False",
                "CLASH_DEV_PREFLIGHT": "true",
            },
            clear=False,
        ):
            with patch(
                "ClashRecruit.services.clash_api_preflight.clash_get"
            ) as mock_get:
                importlib.import_module("ClashRecruit.app")

        mock_get.assert_called_once()


if __name__ == "__main__":
    unittest.main()
