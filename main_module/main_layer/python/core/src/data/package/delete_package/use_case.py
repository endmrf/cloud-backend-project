from collections import namedtuple
from core.src.domain.use_cases import DeletePackageUseCaseInterface
from core.src.infra.repo import PackageRepository

DeletePackageParameter = namedtuple("DeletePackageParameter", "id empresa_id")


class DeletePackageUseCase(DeletePackageUseCaseInterface):
    """
    Use case gateway for delete and existing Package entity
    """

    repository = PackageRepository()

    def proceed(self, parameter: DeletePackageParameter) -> dict:
        """
        Proceed the execution of use case by calling database to delete an existing entity by ID
        :param  - parameter: An Interfaced object with required data
        :return - A Dictionary with formated response of the request having 'success' and 'data' objects
        """

        try:
            record = self.repository.get_package(
                id=parameter.id, empresa_id=parameter.empresa_id
            )

            success = self.repository.delete_package(
                id=parameter.id, empresa_id=parameter.empresa_id
            )
            serialized_record = record._asdict()
            return self._render_response(success, serialized_record)
        except:
            return self._render_response(False, None)
