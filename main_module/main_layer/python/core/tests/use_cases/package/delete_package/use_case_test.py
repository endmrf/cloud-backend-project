import os
import uuid
import pytest
from faker import Faker
from unittest import mock
from core.tests.mock_util import MockUtil, MockTools
from core.src.infra.config import DBConnectionHandler
from core.src.data.package.delete_package import (
    DeletePackageUseCase,
    DeletePackageParameter,
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
def test_delete_use_case(mock_entity, db_connection_handler):
    """
    Test the DeletePackageUseCase invocation
    :param - None
    :return - None
    """

    empresa_id = mock_entity["empresa_id"]
    engine = db_connection_handler.get_engine()
    engine.execute(MockUtil.build_insert_sql("packages", mock_entity))

    use_case = DeletePackageUseCase()
    parameter = DeletePackageParameter(id=mock_entity["id"], empresa_id=empresa_id)
    response = use_case.proceed(parameter)

    assert response["success"] is True
    assert response["data"] is not None
    data = response["data"]

    assert data["id"] == mock_entity["id"]

    parameter = DeletePackageParameter(id="<NOT_EXISTING_ID>", empresa_id=empresa_id)
    response = use_case.proceed(parameter)

    assert response["success"] is False
    assert response["data"] is None

    query_entity = engine.execute(
        "SELECT * FROM packages WHERE id='{}'".format(mock_entity["id"])
    ).fetchone()

    assert query_entity is None
