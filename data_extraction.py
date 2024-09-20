import pandas as pd
import numpy as np
import yaml
from sqlalchemy import create_engine, inspect
import psycopg2
import tabula as tb
import requests
import json
import boto3

class DataExtractor:
    def __init__(self):
        pass


    def read_rds_table(self, table_names, table_name, engine):

        engine = engine.connect() # Connect to the database engine

        data = pd.read_sql_table(table_name, engine) # Read a specific table into the df
        return data 
        
    def retrieve_pdf_data(self, link):
        pdf_path = link
        df = tb.read_pdf(pdf_path, pages="all") # Read all pages of the PDF into the df
        df = pd.concat(df) # Merges all PDF dfs into one 
        df = df.reset_index(drop=True)
        return df

    def list_number_of_stores(self, endpoint, api_key):
        response = requests.get(endpoint, headers=api_key) # Make a get request to the API endpoint to get the number of stores
        content = response.text
        result = json.loads(content) # Parse JSON response
        number_stores = result['number_stores'] # Extract number of stores
        
        return number_stores

    def retrieve_stores_data(self, number_stores, endpoint, api_key):
        data = []
        for store in range(0, number_stores): # Loop through the number of stores and retrieve data for each
            response = requests.get(f'{endpoint}{store}', headers=api_key)
            content = response.text
            result = json.loads(content)
            data.append(result) # Append store data to list

        df = pd.DataFrame(data) # Convert list of data to a df
        return df
    
    def extract_from_s3(self, s3_address):
        s3 = boto3.resource('s3') # Create an S3 resource
        # Clean up the S3 address format
        if 's3://' in s3_address:
            s3_address = s3_address.replace('s3://','' )
        elif 'https' in s3_address:
            s3_address = s3_address.replace('https://', '')

        # Split the address into bucket name and file key
        bucket_name, file_key = s3_address.split('/', 1)
        bucket_name = 'data-handling-public'
        obj = s3.Object(bucket_name, file_key) # Gets the S3 object
        body = obj.get()['Body'] # Reads the body of the object
        # Loads data based on file type
        if 'csv' in file_key:
            df = pd.read_csv(body)
        elif '.json' in file_key:
            df = pd.read_json(body)
        df = df.reset_index(drop=True)
        return df


extractor = DataExtractor()