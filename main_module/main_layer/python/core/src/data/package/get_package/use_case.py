from collections import namedtuple
from core.src.domain.use_cases import GetPackageUseCaseInterface
from core.src.infra.repo import PackageRepository

GetPackageParameter = namedtuple("GetPackageParameter", "id empresa_id")


class GetPackageUseCase(GetPackageUseCaseInterface):
    """
    Use case gateway for get single Package entity
    """

    package_repository = PackageRepository()

    def proceed(self, parameter: GetPackageParameter) -> dict:
        """
        Proceed the execution of use case by calling database to retrieve single entity by ID
        :param  - parameter: An Interfaced object with required data
        :return - A Dictionary with formated response of the request having 'success' and 'data' objects
        """

        try:
            record = self.package_repository.get_package(
                id=parameter.id, empresa_id=parameter.empresa_id
            )
            serialized_record = record._asdict()
            return self._render_response(True, serialized_record)
        except:
            return self._render_response(False, None)
