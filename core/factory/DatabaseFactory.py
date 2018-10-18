from services.MongoDB import MongoDB
from config import LocalHostConfig as config

_db_instances = {
    'mongodb': MongoDB(),
}

def get_database():
    return _db_instances[config.DATABASE_TYPE]