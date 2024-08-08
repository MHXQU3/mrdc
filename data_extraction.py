from sqlalchemy import create_engine, inspect
import yaml 
import pandas as pd
import psycopg2
from database_utils import DatabaseConnector

class DataExtractor:
   
    def __init__(self, db_connector):
        self.db_connector = db_connector
        self.engine = db_connector.init_db_engine()

    def list_tables(self):
        return self.db_connector.list_db_tables(self.engine)

    def read_rds_table(self, table_name):
        """Extracts the specified table from the RDS database as a pandas DataFrame."""
        # List available tables
        available_tables = self.list_tables()
        
        # Check if the table name exists in the list
        if table_name in available_tables:
            # Extract data from the table into a DataFrame
            connection = self.engine.connect()
            data = pd.read_sql_table(table_name, connection)
            connection.close()
            return data
        else:
            raise ValueError(f"Table '{table_name}' does not exist in the database.")

    def extract_user_data(self):
        """Finds and extracts user data from the database."""
        # Assuming the user data table contains 'user' in its name
        available_tables = self.list_tables()
        user_table_name = next((table for table in available_tables if 'user' in table.lower()), None)
        
        if user_table_name:
            return self.read_rds_table(user_table_name)
        else:
            raise ValueError("No table containing user data found in the database.")

connector = DatabaseConnector('db_creds.yaml')
extractor = DataExtractor(connector)

# Extract user data
user_data_df = extractor.extract_user_data()
print(user_data_df.head())