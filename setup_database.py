import sys 
import os
import importlib
from unittest import mock 

MOCK_SQLITE_PATH: str = f"sqlite:///mock_data.db"
MODULE_PATH: str = "main_module/main_layer/python/core"

sys.path.append(os.path.dirname(MODULE_PATH))
mname = os.path.splitext(os.path.basename(MODULE_PATH))[0]
imported = importlib.import_module(mname)                       
sys.path.pop()

from core.src.infra.config import *
from core.src.infra.entities import *

@mock.patch.dict(os.environ, {"TEST_DATABASE_CONNECTION": MOCK_SQLITE_PATH})
def generate_tables():    
    conn = DBConnectionHandler()
    engine = conn.get_engine()
    Base.metadata.create_all(engine)

generate_tables()