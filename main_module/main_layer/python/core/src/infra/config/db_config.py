import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


class DBConnectionHandler:
    """Sqlalchemy database connection"""

    def __init__(self, connection_string: str = None):

        self.log_enabled = os.getenv("LOG_AURORA") == "ENABLED"
        self.cluster_arn = os.getenv("AURORA_CLUSTER_ARN")
        self.secret_arn = os.getenv("AURORA_SECRET_ARN")
        self.database_name = os.getenv("AURORA_DATABASE_NAME")
        self.__connection_string = "postgresql+auroradataapi://:@/{}".format(
            self.database_name
        )

        if self.___has_test_database_environment():
            self.__connection_string = os.getenv("TEST_DATABASE_CONNECTION")

        if connection_string is not None:
            self.__connection_string = connection_string

        self.session: sessionmaker = None

    def ___is_aurora_serverless_available(self) -> bool:
        """Returna Se banco de dados aurora esta disponível
        :parram - None
        :return - bool: Se banco de dados aurora esta disponível
        """

        return self.cluster_arn is not None and self.secret_arn is not None

    def ___has_test_database_environment(self) -> bool:
        """Retorna se existe variavel de ambiente para banco de dados para testes
        :parram - None
        :return - bool: Se existe variavel de ambiente para banco de dados para testes
        """

        env_var_name = "TEST_DATABASE_CONNECTION"
        return os.getenv(env_var_name) is not None and os.getenv(env_var_name)

    def get_engine(self):
        """Return connection Engine
        :parram - None
        :return - engine connection to Database
        """

        if self.___is_aurora_serverless_available():
            return create_engine(
                self.__connection_string,
                echo=self.log_enabled,
                connect_args=dict(
                    aurora_cluster_arn=self.cluster_arn, secret_arn=self.secret_arn
                ),
            )

        return self._create_engine_sqlite()

    def _create_engine_sqlite(self):
        engine = create_engine(self.__connection_string, echo=self.log_enabled)
        event.listen(engine, "connect", self._fk_pragma_on_connect)
        return engine

    def __enter__(self):
        engine = self.get_engine()
        session_maker = sessionmaker()
        self.session = session_maker(bind=engine)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()  # pylint: disable=no-member

    def _fk_pragma_on_connect(self, dbapi_con, con_record):
        dbapi_con.execute("pragma foreign_keys=ON")
