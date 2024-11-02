from collections import namedtuple
from core.src.domain.use_cases import ListPackagesUseCaseInterface
from core.src.infra.repo import PackageRepository

ListPackagesParameter = namedtuple(
    "ListPackageParam",
    """
        empresa_id 
        name 
        symbol
        column
        order
        page
        limit
    """,
)


class ListPackagesUseCase(ListPackagesUseCaseInterface):
    """
    Use case gateway for list Package entity
    """

    repository = PackageRepository()

    def proceed(self, parameter: ListPackagesParameter) -> dict:
        """
        Proceed the execution of use case by calling database to retrieve entities
        :param  - parameter: An Interfaced object with required data
        :return - A Dictionary with formated response of the request having 'success' and 'data' objects
        """

        name: str = parameter.name if parameter.name is not None else ""
        symbol: str = parameter.symbol if parameter.symbol is not None else ""
        column: str = parameter.column if parameter.column is not None else "created_at"
        order: str = parameter.order if parameter.order is not None else "desc"

        try:
            records = self.repository.select_packages(
                empresa_id=parameter.empresa_id,
                name=name,
                symbol=symbol,
                column=column,
                order=order,
                page=parameter.page,
                limit=parameter.limit,
            )
            total_count = self.repository.count_packages(
                empresa_id=parameter.empresa_id, name=name, symbol=symbol
            )
            serialized_records = list(map(lambda item: item._asdict(), records))
            return self._render_response(True, serialized_records, total=total_count)
        except:
            return self._render_response(False, [])
