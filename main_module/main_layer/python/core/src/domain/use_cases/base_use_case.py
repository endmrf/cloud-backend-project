import os
import traceback
import json
import datetime
import decimal
import jsonschema
from typing import List
from abc import ABC, abstractmethod

from core.src.infra.entities.partner.entity import PartnerRepresentative


class ValidateResponse:
    def __init__(self, success: bool, errors: List[str] = []) -> None:
        self.success = success
        self.errors = errors


class BaseUseCaseInterface(ABC):
    """Interface base para interfaces de casos de uso"""

    @abstractmethod
    def proceed(self, parameters) -> dict:
        """Proceed a use case"""

        raise Exception("Should implement method: proceed")

    def _render_response(self, sucess: bool, data, **extra_data) -> dict:
        """
        Generate a dictionary with formated response using response parameters
        :param  - success: A boolean having success of the request action
                - data: A dictionarie with serialized values having (str, int, float, list, dict)
                - extra_data: An optional extra key-word arguments(dict) with desired extra
                    attributes and values into the formated response
        :return - A Dictionary with formated response of the request having 'success' and 'data' objects
        """

        response = {"success": sucess, "data": data}

        if extra_data:
            for key in extra_data:
                response[key] = extra_data[key]

        return response

    def _print_exception(self) -> None:
        """
        Prints reason from possible raised error or exception using traceback and based on LOG=ENABLED env var
        :param  - None
        :return - None
        """

        if os.getenv("LOG") == "ENABLED":
            traceback.print_exc()

    def _print_log(self, target: any) -> None:
        """
        Prints target object in logs based on LOG=ENABLED env var
        :param  - target: Any object or string that wants to print on logs when LOG env var is enabled
        :return - None
        """

        if os.getenv("LOG") == "ENABLED":
            print("[LOG] - {}".format(target))

    def serialize(self, data: dict) -> dict:
        """
        Inside dictionary, this method transforms every non serializable values like datetime and decimal into serializable values like string and numbers.
        :param  - data: A Dictionary with values
        :return - A Dictionary with serialized values
        """

        json_stringify = json.dumps(data, cls=SerializableEncoder)
        return json.loads(json_stringify)

    def stringify(self, data: dict) -> str:
        """
        Inside dictionary, this method transforms every non serializable values like datetime and decimal into serializable values like string and numbers.
        :param  - data: A Dictionary with values
        :return - A JSON String with serialized values
        """

        return json.dumps(data, cls=SerializableEncoder)

    @classmethod
    def validate_schema(
        cls, type_name: str, instance_data: dict, schema: dict
    ) -> ValidateResponse:
        """
        Validates schema attributes for a given dictionary using jsonschema
        :param  - type_name: The name of validated instance
                - instance_data: A dictionary data with attibutes to validate
                - schema: A dictionary with json schema of desired attributes format of instance_data
        :return - A response object having operation result and possible erros found
        """

        if schema is None:
            raise Exception("EntityValidate", "<schema> not implemented")

        response = cls.__validate_with_draft(type_name, instance_data, schema)
        if response.success:
            return cls.__default_validate(type_name, instance_data, schema)

        return response

    def convert_date_string_to_seconds(cls, date_string: str) -> int:

        date_string = str(date_string.replace("-03:00", ""))
        if "." in date_string:
            date_string = date_string.split(".")[0]
        date = datetime.datetime.strptime(
            str(date_string).replace("-03:00", ""), "%Y-%m-%d %H:%M:%S"
        )
        return int((date - datetime.datetime(1970, 1, 1)).total_seconds())

    @classmethod
    def __validate_with_draft(
        cls, type_name: str, instance_data: dict, schema: dict
    ) -> ValidateResponse:
        """
        Validates schema attributes for a given dictionary using jsonschema draft validation
        :param  - type_name: The name of validated instance
                - instance_data: A dictionary data with attibutes to validate
                - schema: A dictionary with json schema of desired attributes format of instance_data
        :return - A response object having operation result and possible erros found
        """

        errors = []
        draft = jsonschema.Draft7Validator(schema)
        for error in sorted(draft.iter_errors(instance_data), key=str):
            errors.append(
                {
                    "entity": type_name,
                    "field": error.path.pop()
                    if len(error.path) > 0
                    else error.message.split("'")[1].split("'")[0],
                    "type": "invalid",
                    "msg": error.message,
                }
            )

        return ValidateResponse(success=(len(errors) == 0), errors=errors)

    @classmethod
    def __default_validate(
        cls, type_name: str, instance_data: dict, schema: dict
    ) -> ValidateResponse:
        """
        Validates schema attributes for a given dictionary using jsonschema default validation
        :param  - type_name: The name of validated instance
                - instance_data: A dictionary data with attibutes to validate
                - schema: A dictionary with json schema of desired attributes format of instance_data
        :return - A response object having operation result and possible erros found
        """

        try:
            jsonschema.validate(instance_data, schema)
            return ValidateResponse(success=True, errors=[])
        except Exception as e:
            return ValidateResponse(
                success=False,
                errors=[{"entity": type_name, "type": "invalid", "msg": str(e)}],
            )


class SerializableEncoder(json.JSONEncoder):
    """An encoder to serialize values for a valid json format"""

    def __is_datetime(self, instance: any) -> bool:
        """
        Check if instance is a datetime object.
        :param  - instance: A possible datetime value
        :return - If instance is a datetime
        """

        return isinstance(instance, datetime.datetime)

    def __is_decimal(self, instance: any) -> bool:
        """
        Check if instance is a datetime object.
        :param  - instance: A possible datetime value
        :return - If instance is a datetime
        """
        return isinstance(instance, decimal.Decimal)

    def __is_decimal_datetime(self, instance: decimal.Decimal) -> bool:
        """
        Check if instance is eligible to parse to datetime.
        :param  - instance: A decimal value
        :return - If instance is elibible to parse to datetime
        """
        string_value = str(instance)
        clean_value = string_value.split(".")[0]
        return self.__is_decimal(instance) and len(clean_value) >= 9

    def __is_decimal_float(self, instance: decimal.Decimal) -> bool:
        """
        Check if instance is eligible to parse to float.
        :param  - instance: A decimal value
        :return - If instance is elibible to parse to float
        """
        return "." in str(instance)

    def __parse_datetime_to_string(self, instance: datetime.datetime) -> str:
        """
        Parse an datetime value to string with format 'YYYY-mm-dd HH:MM:SS'.
        :param  - instance: A datetime value
        :return - A datetime formated string
        """
        return instance.strftime("%Y-%m-%d %H:%M:%S").split(".")[0]

    def __parse_decimal_to_datetime(
        self, instance: decimal.Decimal
    ) -> datetime.datetime:
        """
        Parse an decimal value to datetime.
        :param  - instance: A datetime value
        :return - A datetime value
        """
        return datetime.datetime.fromtimestamp(float(instance))

    def __parse_decimal_datetime_to_string(self, instance: decimal.Decimal) -> str:
        """
        Parse an decimal datetime seconds value to a datetime string with format 'YYYY-mm-dd HH:MM:SS'.
        :param  - instance: A decimal seconds value
        :return - A datetime formated string
        """
        return self.__parse_datetime_to_string(
            self.__parse_decimal_to_datetime(instance)
        )

    def default(self, instance):
        """
        Parse any non serializable instance value to serializable value.
        :param  - instance: Any non serializable value
        :return - A serializable value like string, numbers ...
        """
        
        if isinstance(instance, PartnerRepresentative):
            return instance.to_dict()

        if self.__is_datetime(instance):
            return self.__parse_datetime_to_string(instance)

        if self.__is_decimal_datetime(instance):
            if self.__is_decimal_datetime(instance):
                return self.__parse_decimal_datetime_to_string(instance)
            elif self.__is_decimal_float(instance):
                return float(instance)
            else:
                return int(instance)

        return super(SerializableEncoder, self).default(instance)
