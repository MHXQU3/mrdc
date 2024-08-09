from sqlalchemy import create_engine, inspect
import yaml 
import psycopg2

class DatabaseConnector:

    def __init__(self, path):
        self.path = path
    
    def read_db_creds(self):
        with open(self.path, 'r') as file:
            db_creds = yaml.safe_load(file)
        return db_creds
    
    def init_db_engine(self):
        db_creds = self.read_db_creds()
        HOST = db_creds.get('RDS_HOST')
        PASSWORD = db_creds.get('RDS_PASSWORD')
        USER = db_creds.get('RDS_USER')
        DATABASE = db_creds.get('RDS_DATABASE')
        PORT = db_creds.get('RDS_PORT')
        DBTYPE = db_creds.get('RDS_DATABASE_TYPE')
        DBAPI = db_creds.get('DBAPI')

        url = f'{DBTYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'
        engine = create_engine(url)
        return engine
    
    def list_db_tables(self, engine):
        with engine.connect() as connection:
            inspector = inspect(connection)
            tables = inspector.get_table_names()
            return tables 
