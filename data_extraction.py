from sqlalchemy import create_engine, inspect
import yaml 
import pandas as pd
import psycopg2
from database_utils import DatabaseConnector

class DataExtractor:
   
    def __init__(self, db_connector):
        self.db_connector = db_connector

    def read_rds_table(self, table_name):
        engine = self.db_connector.init_db_engine()
        data = pd.read_sql_table(table_name, engine)
        return data

    def extract_user_data(self, table_name):
        return self.read_rds_table(table_name)
    
connector = DatabaseConnector('db_creds.yaml')
extractor = DataExtractor(connector)

# Extract user data
user_data_df = extractor.extract_user_data('legacy_users')
print(user_data_df.head())