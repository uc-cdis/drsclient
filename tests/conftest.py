import pytest
import cdisutilstest.code.conftest as cdisutilstest_conftest
from cdisutilstest.code.conftest import (
    indexd_server,
    indexd_client,
    setup_database,
    create_user,
)
from drsclient.client import DrsClient
from indexd.alias.drivers.alchemy import Base as alias_base
from indexd.auth.drivers.alchemy import Base as auth_base
from indexd.default_settings import settings as indexd_settings
from indexd.index.drivers.alchemy import Base as index_base

# indexd's Postgres auto-migration runs alembic, whose alembic.ini/migrations aren't
# shipped in the installed package. Tables are created by setup_database() instead.
indexd_settings["AUTO_MIGRATE"] = False


def clear_database():
    """
    FK-safe replacement for cdisutilstest's clear_database, which deletes parent
    tables before children. That only worked on SQLite (indexd<=3.x test default).
    """
    for base, driver in (
        (index_base, indexd_settings["config"]["INDEX"]["driver"]),
        (alias_base, indexd_settings["config"]["ALIAS"]["driver"]),
        (auth_base, indexd_settings["auth"]),
    ):
        with driver.session as session:
            for table in reversed(base.metadata.sorted_tables):
                session.execute(table.delete())


cdisutilstest_conftest.clear_database = clear_database


@pytest.fixture(scope="function")
def index_client(indexd_client):
    return indexd_client


@pytest.fixture(scope="function")
def drs_client(indexd_server):
    """
    Returns a DrsClient. This will delete any documents,
    aliases, or users made by this
    client after the test has completed.
    Currently the default user is the admin user
    Runs once per test.
    """
    client = DrsClient(baseurl=indexd_server.baseurl, auth=create_user("user", "user"))
    yield client
    clear_database()


@pytest.fixture(scope="function")
def drsclient(drs_client):
    return drs_client
