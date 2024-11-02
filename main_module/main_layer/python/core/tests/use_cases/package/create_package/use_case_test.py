import os
import uuid
import pytest
import datetime
from faker import Faker
from unittest import mock
from core.src.infra.config import DBConnectionHandler
from core.src.data.package.create_package import (
    CreatePackageUseCase,
    CreatePackageParameter,
)
from core.tests.mock_util import MockTools

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
def test_create_use_case(mock_entity, db_connection_handler):
    """
    Test the CreatePackageUseCase invocation
    :param - None
    :return - None
    """

    empresa_id = mock_entity["empresa_id"]
    use_case = CreatePackageUseCase()

    parameter = CreatePackageParameter(
        name=mock_entity["name"],
        symbol=mock_entity["symbol"],
        empresa_id=empresa_id,
        created_by=mock_entity["created_by"],
        updated_by=mock_entity["updated_by"],
        created_at=datetime.datetime.strptime(
            mock_entity["created_at"], "%Y-%m-%d %H:%M:%S"
        ),
        updated_at=datetime.datetime.strptime(
            mock_entity["updated_at"], "%Y-%m-%d %H:%M:%S"
        ),
    )
    response = use_case.proceed(parameter)
    assert response["success"] is True
    assert response["data"] is not None

    data = use_case.serialize(response)["data"]

    engine = db_connection_handler.get_engine()
    query_entity = engine.execute(
        "SELECT * FROM packages WHERE id='{}'".format(response["data"]["id"])
    ).fetchone()

    assert data["name"] == query_entity.name
    assert data["symbol"] == query_entity.symbol
    assert data["empresa_id"] == query_entity.empresa_id
    assert data["created_by"] == query_entity.created_by
    assert data["updated_by"] == query_entity.updated_by
    assert data["created_at"] == query_entity.created_at.split(".")[0]
    assert data["updated_at"] == query_entity.updated_at.split(".")[0]

    engine.execute("DELETE FROM packages WHERE empresa_id='{}'".format(empresa_id))
