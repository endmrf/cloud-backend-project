# pylint: disable=E1101

import uuid
from datetime import datetime, timezone, timedelta
from typing import List
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import String
from core.src.data.interfaces import PackageRepositoryInterface
from core.src.domain.models import Package
from core.src.infra.config import DBConnectionHandler
from core.src.infra.entities import Package as PackageModel


class PackageRepository(PackageRepositoryInterface):
    """Class to manage Package Repository"""

    @classmethod
    def __build_entity_to_domain_interface(
        cls, entity_instance: PackageModel
    ) -> Package:
        """
        Transform infra Entity Package into named tuple domain model Package
        :param  - entity_instance: A PackageModel
        :return - A domain Package
        """

        domain_entity = Package(
            id=entity_instance.id,
            name=entity_instance.name,
            symbol=entity_instance.symbol,
            empresa_id=entity_instance.empresa_id,
            created_by=entity_instance.created_by,
            updated_by=entity_instance.updated_by,
            created_at=str(entity_instance.created_at),
            updated_at=str(entity_instance.updated_at),
        )
        return domain_entity

    @classmethod
    def create_package(
        cls,
        name: str,
        symbol: str,
        empresa_id: str,
        created_by: str = None,
        updated_by: str = None,
        created_at: datetime = datetime.now(timezone(timedelta(hours=-3))),
        updated_at: datetime = datetime.now(timezone(timedelta(hours=-3))),
    ) -> Package:
        """
        Create new Package
        :param  - name: The name of the Package
                - symbol: The symbol of the Package
                - empresa_id: ID of the Package's company doing create action
                - created_by: ID of the Package doing create action, (default is None)
                - created_at: Datetime of create action, (default is now())
                - updated_by: ID of the Package doing update action, (default is None)
                - updated_at: Datetime of update action, (default is now())
        :return - A Package created
        """

        with DBConnectionHandler() as db_connection:
            try:
                id = str(uuid.uuid4())
                entity_instance = PackageModel(
                    id=id,
                    name=name,
                    symbol=symbol,
                    empresa_id=empresa_id,
                    created_at=created_at,
                    created_by=created_by,
                    updated_by=updated_by,
                    updated_at=updated_at,
                )
                db_connection.session.add(entity_instance)
                db_connection.session.commit()

                return cls.__build_entity_to_domain_interface(entity_instance)

            except:
                db_connection.session.rollback()
                raise
            finally:
                db_connection.session.close()

        return None

    @classmethod
    def update_package(
        cls,
        id: str,
        name: str,
        symbol: str,
        empresa_id: str,
        created_by: str = None,
        updated_by: str = None,
        created_at: datetime = datetime.now(timezone(timedelta(hours=-3))),
        updated_at: datetime = datetime.now(timezone(timedelta(hours=-3))),
    ) -> Package:
        """
        Update data in Package
        :param  - id: ID of the Package
                - name: The name of the Package
                - symbol: The symbol of the Package
                - empresa_id: ID of the Package's company doing create action
                - created_by: ID of the Package doing create action, (default is None)
                - created_at: Datetime of create action, (default is now())
                - updated_by: ID of the Package doing update action, (default is None)
                - updated_at: Datetime of update action, (default is now())
        :return - A Package updated
        """

        with DBConnectionHandler() as db_connection:
            try:
                entity_instance = db_connection.session.get(PackageModel, id)
                entity_instance.name = name
                entity_instance.symbol = symbol
                entity_instance.updated_by = updated_by
                entity_instance.updated_at = updated_at

                db_connection.session.merge(entity_instance)
                db_connection.session.commit()

                return cls.__build_entity_to_domain_interface(entity_instance)
            except:
                db_connection.session.rollback()
                raise
            finally:
                db_connection.session.close()

        return None

    @classmethod
    def delete_package(cls, id: str, empresa_id: str) -> bool:
        """
        Delete Package by ID
        :param  - id: ID of the Package
                - empresa_id: ID of the Package company
        :return - If deletion has been succeeded
        """

        with DBConnectionHandler() as db_connection:
            try:
                entity_instance = (
                    db_connection.session.query(PackageModel)
                    .filter(
                        PackageModel.id == id, PackageModel.empresa_id == empresa_id
                    )
                    .first()
                )
                db_connection.session.delete(entity_instance)
                db_connection.session.commit()
                return True
            except:
                db_connection.session.rollback()
                raise
            finally:
                db_connection.session.close()

        return False

    @classmethod
    def select_packages(
        cls,
        empresa_id: str,
        name: str = "",
        symbol: str = "",
        column: str = "created_at",
        order: str = "desc",
        limit: int = 10,
        page: int = 0,
    ) -> List[Package]:
        """
        Search Package by company and filter by name and/or desciption
        :param  - empresa_id: ID of the Package company
                - name: The name of the Package
                - symbol: The symbols of the Package
                - column: (Optional) The column name where is desired to order results. Default is 'created_at' attribute
                - order: (Optional) The order where is desired to order results 'asc|desc'. Default is 'desc'
                - limit: (Optional) The total count of found records. Default is 10
                - page: (Optional) The index of current page requestes. Default is 0
        :return - List of found Package
        """

        attribute = getattr(PackageModel, column)
        order_by_attribute = attribute.desc() if order == "desc" else attribute.asc()
        query_data = None

        with DBConnectionHandler() as db_connection:
            try:
                query_data = (
                    db_connection.session.query(PackageModel)
                    .filter(
                        PackageModel.empresa_id == empresa_id,
                        PackageModel.name.ilike("%" + name + "%"),
                        PackageModel.symbol.ilike("%" + symbol + "%")
                        if symbol != ""
                        else True,
                    )
                    .order_by(order_by_attribute)
                    .limit(limit)
                    .offset(page)
                ).all()
                return list(
                    map(
                        lambda instance: cls.__build_entity_to_domain_interface(
                            instance
                        ),
                        query_data,
                    )
                )
            except NoResultFound:
                return []
            except:
                db_connection.session.rollback()
                raise
            finally:
                db_connection.session.close()

    @classmethod
    def count_packages(self, empresa_id: str, name: str = "", symbol: str = "") -> int:
        """
        Retrieve count of results in query by company and filter by key attributes
        :param  - empresa_id: ID of Package company
                - name: The name of Package
        :return - A total count of query result
        """

        with DBConnectionHandler() as db_connection:
            try:
                count = (
                    db_connection.session.query(PackageModel)
                    .filter(
                        PackageModel.empresa_id == empresa_id,
                        PackageModel.name.ilike("%" + name + "%"),
                        PackageModel.symbol.ilike("%" + symbol + "%")
                        if symbol != ""
                        else True,
                    )
                    .count()
                )
                return count
            except NoResultFound:
                return []
            except:
                db_connection.session.rollback()
                raise
            finally:
                db_connection.session.close()

    @classmethod
    def get_package(cls, id: str, empresa_id: str) -> Package:
        """
        Retrieve Package by ID and company ID
        :param  - id: ID of the Package
                - empresa_id: ID of the Package company
        :return - A found Package by ID
        """

        query_data = None
        with DBConnectionHandler() as db_connection:
            try:
                query_data = (
                    db_connection.session.query(PackageModel).filter(
                        PackageModel.id == id, PackageModel.empresa_id == empresa_id
                    )
                ).first()
                if query_data is not None:
                    return cls.__build_entity_to_domain_interface(query_data)
            except NoResultFound:
                return []
            except:
                db_connection.session.rollback()
                raise
            finally:
                db_connection.session.close()

        return None

    @classmethod
    def select_packages_by_json_name(
        cls,
        empresa_id: str,
        name: str = "",
        symbol: str = "",
        json_data_info: str = None,
    ) -> List[Package]:
        """
        Search Package by company and filter by name and/or desciption
        :param  - empresa_id: ID of Package company
                - name: The name of Package
                - symbol: The symbols of Package
                - json_data_info: Filter by 'info' field into json_data attribute
        :return - List of found Package
        """

        query = (
            PackageModel.empresa_id == empresa_id,
            PackageModel.name.like("%" + name + "%"),
            PackageModel.symbol.like("%" + symbol + "%"),
        )

        if json_data_info is not None:
            query.add(
                PackageModel.json_data["info"]
                .cast(String)
                .like("%" + json_data_info + "%")
            )

        query_data = None
        with DBConnectionHandler() as db_connection:
            try:
                query_data = (
                    db_connection.session.query(PackageModel).filter(query)
                ).all()
                return query_data

            except NoResultFound:
                return []
            except:
                db_connection.session.rollback()
                raise
            finally:
                db_connection.session.close()

        return None
