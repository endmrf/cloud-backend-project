from collections import namedtuple
from core.src.domain.use_cases import CreatePackageUseCaseInterface
from core.src.infra.repo import PackageRepository

CreatePackageParameter = namedtuple(
    "CreatePackageParameter",
    "name symbol empresa_id created_by updated_by created_at updated_at",
)


class CreatePackageUseCase(CreatePackageUseCaseInterface):
    """
    Use case gateway for create a new Package entity
    """

    repository = PackageRepository()

    def proceed(self, parameter: CreatePackageParameter) -> dict:
        """
        Proceed the execution of use case by calling database to create a new single entity with parameters
        :param  - parameter: An Interfaced object with required data
        :return - A Dictionary with formated response of the request having 'success' and 'data' objects
        """

        try:
            record = self.repository.create_package(
                name=parameter.name,
                symbol=parameter.symbol,
                empresa_id=parameter.empresa_id,
                created_by=parameter.created_by,
                updated_by=parameter.updated_by,
                created_at=parameter.created_at,
                updated_at=parameter.updated_at,
            )
            serialized_record = record._asdict()
            return self._render_response(True, serialized_record)
        except:
            self._print_exception()
            return self._render_response(False, None)
