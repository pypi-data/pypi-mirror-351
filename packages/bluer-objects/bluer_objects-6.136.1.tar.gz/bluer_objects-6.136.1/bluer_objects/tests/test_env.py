from bluer_ai.tests.test_env import test_bluer_ai_env

from bluer_objects import env
from bluer_objects.storage.WebDAV import WebDAVInterface
from bluer_objects.storage.WebDAVrequest import WebDAVRequestInterface
from bluer_objects.storage.WebDAVzip import WebDAVzipInterface


def test_required_env():
    test_bluer_ai_env()


def test_bluer_objects_env():
    assert env.ABCLI_MLFLOW_EXPERIMENT_PREFIX

    assert env.BLUER_OBJECTS_STORAGE_INTERFACE in [
        WebDAVInterface.name,
        WebDAVRequestInterface.name,
        WebDAVzipInterface.name,
    ]

    assert env.WEBDAV_HOSTNAME
    assert env.WEBDAV_LOGIN
    assert env.WEBDAV_PASSWORD
