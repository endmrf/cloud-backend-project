import os
import uuid
import pytest
from faker import Faker
from unittest import mock
from core.tests.mock_util import MockUtil, MockTools
from core.src.infra.config import DBConnectionHandler
from core.src.data.package.list_packages import (
    ListPackagesUseCase,
    ListPackagesParameter,
)

fake = Faker()
MOCK_DB_PATH = MockTools.get_mock_db_path()


@pytest.fixture(scope="session")
def mock_entity():
    return {
        "id": str(uuid.uuid4()),
        "empresa_id": str(uuid.uuid4()),
        "name": fake.name(),
        "symbol": fake.text(),
        "created_by": str(uuid.uuid4()),
        "updated_by": str(uuid.uuid4()),
        "created_at": "{} {}".format(fake.date_between("-1y"), fake.time()),
        "updated_at": "{} {}".format(fake.date_between("-1y"), fake.time()),
    }


@pytest.fixture(scope="session")
@mock.patch.dict(os.environ, {"TEST_DATABASE_CONNECTION": MOCK_DB_PATH})
def db_connection_handler():
    return DBConnectionHandler()


@mock.patch.dict(os.environ, {"TEST_DATABASE_CONNECTION": MOCK_DB_PATH})
def test_list_use_case(mock_entity, db_connection_handler):
    """
    Test the ListPackagesUseCase invocation
    :param - None
    :return - None
    """

    empresa_id = mock_entity["empresa_id"]
    engine = db_connection_handler.get_engine()
    engine.execute(MockUtil.build_insert_sql("packages", mock_entity))

    use_case = ListPackagesUseCase()
    parameter = ListPackagesParameter(
        empresa_id=empresa_id,
        name=mock_entity["name"],
        symbol="",
        column="created_at",
        order="desc",
        page=0,
        limit=10,
    )
    response = use_case.proceed(parameter)

    assert response["success"] is True
    assert response["data"] is not None

    assert response["data"][0]["id"] == mock_entity["id"]
    assert response["data"][0]["name"] == mock_entity["name"]
    assert response["data"][0]["symbol"] == mock_entity["symbol"]
    assert response["data"][0]["empresa_id"] == mock_entity["empresa_id"]

    engine.execute("DELETE FROM packages WHERE empresa_id='{}'".format(empresa_id))
