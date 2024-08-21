from sqlalchemy import create_engine, inspect
import yaml 
import pandas as pd
import tabula as tb
import requests
import json
import psycopg2
import boto3
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
    
    def retrieve_pdf_data(self, link):
        pdf_data = tb.read_pdf(link, pages='all', stream=True)
        pdf_data = pd.concat(pdf_data)
        pdf_data = pdf_data.reset_index(drop=True)
        return pdf_data
    
    def list_number_of_stores(self, endpoint, headers):
        response = requests.get(endpoint, headers=headers)
        content = response.text
        result = json.loads(content)
        number_stores = result['number_stores']
        
        return number_stores
    
    def retrieve_stores_data(self, number_stores, endpoint, headers):
        data = []
        for store in range(0, number_stores):
            response = requests.get(f'{endpoint}{store}', headers=headers)
            content = response.text
            store_data = json.loads(content)
            data.append(store_data)

        df = pd.DataFrame(data)

        return df
    
    def extract_from_s3(self, s3_address):
        s3 = boto3.resource('s3')
        if s3_address.startswith('s3://'):
            s3_address = s3_address[len('s3://'):]
        
        bucket_name, file_key = s3_address.split('/', 1)
        obj = s3.Object(bucket_name, file_key)
        body = obj.get()['Body']
        
        # Determine file type
        if file_key.endswith('.csv'):
            df = pd.read_csv(body)
        elif file_key.endswith('.json'):
            df = pd.read_json(body)
        df = df.reset_index(drop=True)
        return df
    
    
connector = DatabaseConnector('db_creds.yaml')
extractor = DataExtractor(connector)

# Extract user data
user_data_df = extractor.extract_user_data('legacy_users')
print(user_data_df.head()) 

# Extract card data
link = "https://data-handling-public.s3.eu-west-1.amazonaws.com/card_details.pdf"
card_data = extractor.retrieve_pdf_data(link)
print(card_data.head())

# Extract number of stores
headers = {"x-api-key": "yFBQbwXe9J3sd6zWVAMrK6lcxxr0q1lr2PT6DDMX"}
stores_endpoint = "https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/store_details"
number_of_stores_endpoint = "https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/number_stores"
num_stores = extractor.list_number_of_stores(number_of_stores_endpoint, headers)
print(f"Number of stores: {num_stores}")

# Retrieve store data
if num_stores:
    store_data_df = extractor.retrieve_stores_data(num_stores, stores_endpoint, headers)
    print(store_data_df.head())

