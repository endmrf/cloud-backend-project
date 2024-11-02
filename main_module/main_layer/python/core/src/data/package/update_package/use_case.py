from collections import namedtuple
from core.src.domain.use_cases import UpdatePackageUseCaseInterface
from core.src.infra.repo import PackageRepository

UpdatePackageParameter = namedtuple(
    "UpdatePackageParameter", "id name symbol empresa_id updated_by updated_at"
)


class UpdatePackageUseCase(UpdatePackageUseCaseInterface):
    """
    Use case gateway for create a new Package entity
    """

    repository = PackageRepository()

    def proceed(self, parameter: UpdatePackageParameter) -> dict:
        """
        Proceed the execution of update use case by calling database to update a existing entity with parameters
        :param  - parameter: An Interfaced object with required data
        :return - A Dictionary with formated response of the request having 'success' and 'data' objects
        """

        try:
            record = self.repository.update_package(
                id=parameter.id,
                name=parameter.name,
                symbol=parameter.symbol,
                empresa_id=parameter.empresa_id,
                updated_by=parameter.updated_by,
                updated_at=parameter.updated_at,
            )
            serialized_record = record._asdict()
            return self._render_response(True, serialized_record)
        except:
            self._print_exception()
            return self._render_response(False, None)
