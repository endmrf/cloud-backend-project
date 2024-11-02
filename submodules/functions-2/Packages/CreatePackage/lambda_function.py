import os
import json
from datetime import datetime, timezone, timedelta
from core.src.data.package.create_package import (
    CreatePackageUseCase,
    CreatePackageParameter,
)

CORENAMESPACE = os.environ['CORE_NAMESPACE']
NAMESPACE = os.environ['NAMESPACE']
MODULE = os.environ['MODULE']
REGION = os.environ['REGION']

BODY_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "PackageSchema",
	"type": "object",
	"properties": {
		"name": { "type": "string", "minLength": 1 },
		"symbol": { "type": ["string", "null"] }
	},
	"required": ["name"]
}

def lambda_handler(event, _):
    print("EVENT -> ", json.dumps(event))

    empresa_id = event['empresa_id']
    entity = 'packages'

    user_data = event["principal"]
    body = event['body']
    use_case = CreatePackageUseCase()

    schema_validate = use_case.validate_schema(entity, body, BODY_SCHEMA)
    if not schema_validate.success:
        return {'success': schema_validate.success, 'ErrorCodes': schema_validate.errors}
    
    parameter = CreatePackageParameter(
        name=body["name"],
        symbol=None if 'symbol' not in body else body["symbol"],
        empresa_id=empresa_id,
        created_by=user_data["id"],
        updated_by=user_data["id"],
        created_at=('{}'.format(datetime.now(timezone(timedelta(hours=-3))), "%Y-%m-%dT%H:%M:%S")).split('.')[0],
        updated_at=('{}'.format(datetime.now(timezone(timedelta(hours=-3))), "%Y-%m-%dT%H:%M:%S")).split('.')[0],
    )
    response = use_case.proceed(parameter)

    if response['success']:
        data = use_case.serialize(response)["data"]
        return {
            'success': True, 
            'msg': "Embalagem cadastrada com sucesso", 
            'data': data
        }
    else:
        return {
            'success': False, 
            'data': response['data'], 
            'ErrorCodes': ['entity.save.error']
        }
