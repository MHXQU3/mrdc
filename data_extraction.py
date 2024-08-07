from sqlalchemy import create_engine, inspect
import yaml 
import pandas as pd
import psycopg2

class DataExtractor:
   
    def __init__(self):
        pass

    def read_rds_table(self, engine, tables):
        connection = engine.connect()
        data = pd.read_sql_table(tables, connection)
        return data