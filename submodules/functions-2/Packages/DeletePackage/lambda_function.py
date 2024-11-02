import os
import json
from core.src.data.package.delete_package import (
    DeletePackageUseCase,
    DeletePackageParameter,
)

client = None

CORENAMESPACE = os.environ['CORE_NAMESPACE']
NAMESPACE = os.environ['NAMESPACE']
MODULE = os.environ['MODULE']

def lambda_handler(event, context):
    print("EVENT -> ", json.dumps(event))

    empresa_id = event['empresa_id']
    entity_id = event['id']

    use_case = DeletePackageUseCase()
    parameter = DeletePackageParameter(
        id=entity_id, empresa_id=empresa_id
    )
    response = use_case.proceed(parameter)
    
    if response['success']:
        return {
            'success': True, 
            'msg': 'Embalagem foi removida com sucesso.'
        }
    else:
        return {
            'success': False, 
            'msg': 'Erro ao remover Embalagem'
        }