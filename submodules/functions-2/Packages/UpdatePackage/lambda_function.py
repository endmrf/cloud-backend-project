import json
import os
from datetime import datetime, timezone, timedelta
from core.src.data.package.update_package import (
    UpdatePackageUseCase,
    UpdatePackageParameter,
)

CORENAMESPACE = os.environ['CORE_NAMESPACE']
NAMESPACE = os.environ['NAMESPACE']
MODULE = os.environ['MODULE']
REGION = os.environ['REGION']

BODY_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "UserSchema",
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
    entity_id = event['id']

    user_data = event['principal']
    body = event['body']

    use_case = UpdatePackageUseCase()

    schema_validate = use_case.validate_schema(entity, body, BODY_SCHEMA)
    if not schema_validate.success:
        return {'success': schema_validate.success, 'ErrorCodes': schema_validate.errors}
    
    parameter = UpdatePackageParameter(
        id=entity_id,
        name=body["name"],
        symbol=body["symbol"],
        empresa_id=empresa_id,
        updated_by=user_data["id"],
        updated_at=('{}'.format(datetime.now(timezone(timedelta(hours=-3))), "%Y-%m-%dT%H:%M:%S")).split('.')[0],
    )
    response = use_case.proceed(parameter)

    if response['success']:
        return {
            'success': True, 
            'msg': "Embalagem alterada com sucesso", 
            'data': response['data']
        }
    else:
        return {
            'success': False, 
            'data': response['data']
        }
