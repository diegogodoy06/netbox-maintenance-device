"""Isolated NetBox configuration for local integration tests and CI.

Use only with disposable PostgreSQL and Redis instances.
"""

import os

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
SECRET_KEY = "maintenance-plugin-tests-only-never-use-this-key-in-production"
DATABASE = {
    "NAME": os.environ.get("NETBOX_TEST_DB", "netbox"),
    "USER": os.environ.get("NETBOX_TEST_DB_USER", "netbox"),
    "PASSWORD": os.environ.get("NETBOX_TEST_DB_PASSWORD", "netbox"),
    "HOST": os.environ.get("NETBOX_TEST_DB_HOST", "127.0.0.1"),
    "PORT": int(os.environ.get("NETBOX_TEST_DB_PORT", "5432")),
    "CONN_MAX_AGE": 0,
}
REDIS = {
    "tasks": {
        "HOST": os.environ.get("NETBOX_TEST_REDIS_HOST", "127.0.0.1"),
        "PORT": int(os.environ.get("NETBOX_TEST_REDIS_PORT", "6379")),
        "DATABASE": int(os.environ.get("NETBOX_TEST_REDIS_TASK_DB", "0")),
    },
    "caching": {
        "HOST": os.environ.get("NETBOX_TEST_REDIS_HOST", "127.0.0.1"),
        "PORT": int(os.environ.get("NETBOX_TEST_REDIS_PORT", "6379")),
        "DATABASE": int(os.environ.get("NETBOX_TEST_REDIS_CACHE_DB", "1")),
    },
}
API_TOKEN_PEPPERS = {1: "maintenance-tests-only-token-pepper-never-use-in-production"}
PLUGINS = ["netbox_maintenance_device"]
