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

    def upload_to_db(self, data_frame, table_name, db_creds):
        local_engine = create_engine(f"{db_creds['LOCAL_DATABASE_TYPE']}+{db_creds['LOCAL_DB_API']}://{db_creds['LOCAL_USER']}:{db_creds['LOCAL_PASSWORD']}@{db_creds['LOCAL_HOST']}:{db_creds['LOCAL_PORT']}/{db_creds['LOCAL_DATABASE']}")
        local_engine.connect()
        data_frame.to_sql(table_name, local_engine, if_exists='replace')