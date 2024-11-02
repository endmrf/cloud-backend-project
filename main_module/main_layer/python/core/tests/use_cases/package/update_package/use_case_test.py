import os
import uuid
import pytest
import datetime
from faker import Faker
from unittest import mock
from core.tests.mock_util import MockUtil, MockTools
from core.src.infra.config import DBConnectionHandler
from core.src.data.package.update_package import (
    UpdatePackageUseCase,
    UpdatePackageParameter,
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
def test_update_use_case(mock_entity, db_connection_handler):
    """
    Test the UpdatePackageUseCase invocation
    :param - None
    :return - None
    """

    empresa_id = mock_entity["empresa_id"]
    engine = db_connection_handler.get_engine()
    engine.execute(MockUtil.build_insert_sql("packages", mock_entity))

    name = fake.name()
    symbol = fake.text()
    updated_by = str(uuid.uuid4())
    updated_at = datetime.datetime.now()

    use_case = UpdatePackageUseCase()
    parameter = UpdatePackageParameter(
        id=mock_entity["id"],
        name=name,
        symbol=symbol,
        empresa_id=mock_entity["empresa_id"],
        updated_by=updated_by,
        updated_at=updated_at,
    )
    response = use_case.proceed(parameter)
    assert response["success"] is True
    assert response["data"] is not None

    data = response["data"]

    query_entity = engine.execute(
        "SELECT * FROM packages WHERE id='{}'".format(mock_entity["id"])
    ).fetchone()

    assert data["name"] == query_entity.name
    assert data["symbol"] == query_entity.symbol
    assert data["empresa_id"] == query_entity.empresa_id
    assert data["updated_by"] == query_entity.updated_by
    assert str(data["updated_at"]) == query_entity.updated_at

    parameter = UpdatePackageParameter(
        id="<NOT_EXISTING_ID>",
        name=name,
        symbol=symbol,
        empresa_id=mock_entity["empresa_id"],
        updated_by=updated_by,
        updated_at=updated_at,
    )
    response = use_case.proceed(parameter)
    assert response["success"] is False
    assert response["data"] is None

    engine.execute("DELETE FROM packages WHERE empresa_id='{}'".format(empresa_id))
