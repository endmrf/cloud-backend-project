import json
import os
from lambda_utils import  get_filter
from core.src.data.package.list_packages import (
    ListPackagesUseCase,
    ListPackagesParameter
)
from core.src.data.filter.get_filter import (
    GetFilterUseCase,
    GetFilterParameter
)

CORENAMESPACE = os.environ['CORE_NAMESPACE']
NAMESPACE = os.environ['NAMESPACE']
MODULE = os.environ['MODULE']
FUNCTION_NAME = os.environ['AWS_LAMBDA_FUNCTION_NAME']

def lambda_handler(event, _):
    print("EVENT -> ", json.dumps(event))
    
    empresa_id = event['empresa_id']
    user_data = event["principal"]

    parameter = GetFilterParameter(
        empresa_id=empresa_id,
        entity='table-packages-list',
        user_id=user_data["id"]
    )
    use_case = GetFilterUseCase()
    response = use_case.proceed(parameter)
    filters = response.get('data')
    if filters is not None:
        filters = filters.get('data').get('columns')
    
    offset = int(event['offset']) if len(event['offset']) > 0 else 0
    limit = int(event['limit']) if len(event['limit']) > 0 else 10
    order = event['order'] if len(event['order']) > 0 else None
    orderfield = event['orderfield'] if len(event['orderfield']) > 0 else None
    
    use_case = ListPackagesUseCase()
    parameter = ListPackagesParameter(
        empresa_id=empresa_id, name=event["name"], symbol=event["symbol"], column=orderfield, order=order, page=offset, limit=limit
    )
    response = use_case.proceed(parameter)

    serialized = use_case.serialize(response)
    
    if serialized['success'] == True:
        return {
            'success': True, 
            'data': serialized['data'], 
            'limit': limit,
            'total': serialized['total'], 
            'offset': int(event['offset']) if len(event['offset']) > 0 else 0,
            'columns': filters
        }
    else:
        return {
            'success': False, 
            'data': serialized['data']
        }
        
    