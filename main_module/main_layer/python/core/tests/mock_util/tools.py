import platform


class MockTools:
    @staticmethod
    def get_mock_db_path() -> str:

        return "sqlite:////tmp/mock_data.db"
