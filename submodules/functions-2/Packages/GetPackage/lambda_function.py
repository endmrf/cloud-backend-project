import os
import json
from core.src.data.package.get_package import (
    GetPackageParameter,
    GetPackageUseCase,
)

CORENAMESPACE = os.environ['CORE_NAMESPACE']
NAMESPACE = os.environ['NAMESPACE']
MODULE = os.environ['MODULE']
FUNCTION_NAME = os.environ['AWS_LAMBDA_FUNCTION_NAME']

def lambda_handler(event, _):
    print("EVENT -> ", json.dumps(event))
    
    empresa_id = event['empresa_id']
    entity_id = event['id']

    use_case = GetPackageUseCase()
    parameter = GetPackageParameter(
        id=entity_id,
        empresa_id=empresa_id,
    )
    response = use_case.proceed(parameter)
    
    return use_case.serialize(response)
    