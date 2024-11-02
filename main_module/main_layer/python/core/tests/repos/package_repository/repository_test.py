import os
import json
import uuid
import pytest
from unittest import mock
from faker import Faker
from core.src.infra.repo import PackageRepository
from core.tests.mock_util import MockUtil, MockTools
from core.src.infra.config import DBConnectionHandler


fake = Faker()
MOCK_DB_PATH = MockTools.get_mock_db_path()


def generate_uuid():
    return str(uuid.uuid4())


@pytest.fixture(scope="session")
def mock_entity():
    return {
        "id": str(uuid.uuid4()),
        "empresa_id": str(uuid.uuid4()),
        "name": fake.name(),
        "symbol": fake.text(),
        "created_at": "{} {}".format(fake.date_between("-1y"), fake.time()),
        "updated_at": "{} {}".format(fake.date_between("-1y"), fake.time()),
    }


@pytest.fixture(scope="session")
@mock.patch.dict(os.environ, {"TEST_DATABASE_CONNECTION": MOCK_DB_PATH})
def db_connection_handler():
    return DBConnectionHandler()


@mock.patch.dict(os.environ, {"TEST_DATABASE_CONNECTION": MOCK_DB_PATH})
def test_package_repository_create(mock_entity, db_connection_handler):
    """
    Test the create action into Repository
    :param - None
    :return - None
    """

    empresa_id = mock_entity["empresa_id"]
    package_repository = PackageRepository()

    data = package_repository.create_package(
        name=mock_entity["name"], symbol=mock_entity["symbol"], empresa_id=empresa_id
    )

    engine = db_connection_handler.get_engine()
    query_entity = engine.execute(
        "SELECT * FROM packages WHERE id='{}'".format(data.id)
    ).fetchone()

    assert data.name == query_entity.name
    assert data.symbol == query_entity.symbol
    assert data.empresa_id == query_entity.empresa_id

    engine.execute("DELETE FROM packages WHERE empresa_id='{}'".format(data.empresa_id))


@mock.patch.dict(os.environ, {"TEST_DATABASE_CONNECTION": MOCK_DB_PATH})
def test_package_repository_list(mock_entity, db_connection_handler):
    """
    Test list query action into Repository
    :param - None
    :return - None
    """

    engine = db_connection_handler.get_engine()
    engine.execute(MockUtil.build_insert_sql("packages", mock_entity))
    package_repository = PackageRepository()

    data = package_repository.select_packages(empresa_id=mock_entity["empresa_id"])

    assert len(data) > 0

    data = package_repository.select_packages(
        empresa_id=mock_entity["empresa_id"], name=mock_entity["name"]
    )
    assert len(data) > 0

    assert data[0].id == mock_entity["id"]
    assert data[0].name == mock_entity["name"]
    assert data[0].symbol == mock_entity["symbol"]
    assert data[0].empresa_id == mock_entity["empresa_id"]

    engine.execute(
        "DELETE FROM packages WHERE empresa_id='{}'".format(mock_entity["empresa_id"])
    )


@mock.patch.dict(os.environ, {"TEST_DATABASE_CONNECTION": MOCK_DB_PATH})
def test_package_repository_get(mock_entity, db_connection_handler):
    """
    Test get single INSTANCE action into Repository
    :param - None
    :return - None
    """

    engine = db_connection_handler.get_engine()
    engine.execute(MockUtil.build_insert_sql("packages", mock_entity))

    package_repository = PackageRepository()
    data = package_repository.get_package(
        id=mock_entity["id"], empresa_id=mock_entity["empresa_id"]
    )

    assert data.id == mock_entity["id"]
    assert data.name == mock_entity["name"]
    assert data.symbol == mock_entity["symbol"]
    assert data.empresa_id == mock_entity["empresa_id"]

    engine.execute(
        "DELETE FROM packages WHERE empresa_id='{}'".format(mock_entity["empresa_id"])
    )


@mock.patch.dict(os.environ, {"TEST_DATABASE_CONNECTION": MOCK_DB_PATH})
def test_package_repository_update(mock_entity, db_connection_handler):
    """
    Test update single INSTANCE action into Repository
    :param - None
    :return - None
    """

    engine = db_connection_handler.get_engine()
    engine.execute(MockUtil.build_insert_sql("packages", mock_entity))

    name = fake.name()
    symbol = fake.text()
    updated_by = "UNIT_TEST"

    package_repository = PackageRepository()
    data = package_repository.update_package(
        id=mock_entity["id"],
        name=name,
        symbol=symbol,
        empresa_id=mock_entity["empresa_id"],
        updated_by=updated_by,
    )

    query_entity = engine.execute(
        "SELECT * FROM packages WHERE id='{}'".format(data.id)
    ).fetchone()

    assert data.id == query_entity.id
    assert data.id == mock_entity["id"]
    assert data.name == query_entity.name
    assert data.symbol == query_entity.symbol
    assert data.empresa_id == query_entity.empresa_id
    assert mock_entity["empresa_id"] == query_entity.empresa_id

    assert mock_entity["name"] != query_entity.name
    assert mock_entity["symbol"] != query_entity.symbol

    engine.execute(
        "DELETE FROM packages WHERE empresa_id='{}'".format(mock_entity["empresa_id"])
    )


@mock.patch.dict(os.environ, {"TEST_DATABASE_CONNECTION": MOCK_DB_PATH})
def test_package_repository_delete(mock_entity, db_connection_handler):
    """
    Test delete single INSTANCE action into Repository
    :param - None
    :return - None
    """

    engine = db_connection_handler.get_engine()
    engine.execute(MockUtil.build_insert_sql("packages", mock_entity))

    package_repository = PackageRepository()
    deleted = package_repository.delete_package(
        id=mock_entity["id"], empresa_id=mock_entity["empresa_id"]
    )

    assert deleted is True

    query_entity = engine.execute(
        "SELECT * FROM packages WHERE id='{}'".format(mock_entity["id"])
    ).fetchone()

    assert query_entity is None

    try:
        package_repository.delete_package(
            id="nonexists", empresa_id=mock_entity["empresa_id"]
        )
        assert False
    except:
        assert True
