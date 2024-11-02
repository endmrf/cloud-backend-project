import os
import json
import uuid
import boto3
from faker import Faker
from typing import Dict, List
from datetime import datetime, timedelta, timezone


class MockUtil:

    @staticmethod
    def build_insert_sql(table_name: str, entity: dict) -> str:
        columns = []
        values = []
        for key in entity:
            columns.append(key)
            if isinstance(entity[key], dict) or isinstance(entity[key], list):
                values.append("'" + json.dumps(entity[key]) + "'")
            elif isinstance(entity[key], str):
                values.append("'" + entity[key] + "'")
            elif isinstance(entity[key], int) or isinstance(entity[key], float):
                values.append(str(entity[key]))
            elif entity[key] is None:
                values.append("NULL")
            else:
                values.append(entity[key])
        columns_string = ",".join(columns)
        values_string = ",".join(values)
        return """INSERT INTO {} ({}) VALUES ({});""".format(
            table_name, columns_string, values_string
        )
