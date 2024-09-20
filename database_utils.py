import pandas as pd
import numpy as np
import yaml
from sqlalchemy import create_engine, inspect
import psycopg2
import os

class DatabaseConnector:
    def __init__(self):
        pass

    def read_db_creds(self):
        with open("db_creds.yaml", "r") as f: # Open and read the database credentials from a YAML file
            db_creds = yaml.safe_load(f)
        return db_creds #Take in YAML and return a dict

    def init_db_engine(self, db_creds):
        engine = create_engine(f"{db_creds['RDS_DATABASE_TYPE']}+{db_creds['DB_API']}://{db_creds['RDS_USER']}:{db_creds['RDS_PASSWORD']}@{db_creds['RDS_HOST']}:{db_creds['RDS_PORT']}/{db_creds['RDS_DATABASE']}")
        engine.connect()
        
        # Take in the db_creds output and initialise and return an sqlalchemy database engine
        return engine

    def list_db_tables(self, engine):
        engine.connect()
        inspector = inspect(engine) # Create an inspector object to retrieve database schema information
        table_names = inspector.get_table_names()
        return table_names
        # Using the engine from init_db_engine() list all the tables in the database so you know whhich tables you can extract data from

    def upload_to_db(self, data_frame, table_name, db_creds):
        local_engine = create_engine(f"{db_creds['LOCAL_DATABASE_TYPE']}+{db_creds['LOCAL_DB_API']}://{db_creds['LOCAL_USER']}:{db_creds['LOCAL_PASSWORD']}@{db_creds['LOCAL_HOST']}:{db_creds['LOCAL_PORT']}/{db_creds['LOCAL_DATABASE']}")
        local_engine.connect()
        data_frame.to_sql(table_name, local_engine, if_exists='replace') # Upload the DataFrame to the specified table in the local database, replacing if it already exists