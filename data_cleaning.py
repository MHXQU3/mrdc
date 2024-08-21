import pandas as pd
import numpy as np

from sqlalchemy import create_engine, inspect
import psycopg2

from data_extraction import DataExtractor
from database_utils import DatabaseConnector

class DataCleaning:

    def __init__(self):
        pass

    def clean_user_data(self, user_data_df):
        user_data_df.replace('NULL', np.nan, inplace=True)
        user_data_df.dropna(subset=['date_of_birth', 'email_address', 'user_uuid'], how='any', axis=0, inplace=True)
        
        user_data_df['date_of_birth'] = pd.to_datetime(user_data_df['date_of_birth'], errors='coerce')
        user_data_df['join_date'] = pd.to_datetime(user_data_df['join_date'], errors='coerce')
        
        user_data_df = user_data_df.dropna(subset=['join_date'])

        user_data_df.loc[:, 'phone_number'] = user_data_df['phone_number'].str.replace(r'\W', '', regex=True)
        
        user_data_df = user_data_df.drop_duplicates(subset=['email_address'])
        user_data_df.drop(user_data_df.columns[0], axis=1, inplace=True)

        user_data_df.to_csv("users.csv", index=False)
        return user_data_df 
    
    def clean_card_data(self, card_data):
        card_data.replace('NULL', np.NaN, inplace=True)
        card_data.dropna(subset=['card_number'], inplace=True)
        card_data['card_number'] = card_data['card_number'].str.replace(r'\D', '', regex=True)
        card_data = card_data[~card_data['card_number'].str.contains('[a-zA-Z?]', na=False)]
        return card_data
    
    def clean_store_data(self, store_data):
        store_data = store_data.reset_index(drop=True)
        store_data.replace('NULL', np.NaN, inplace=True)
        store_data['opening_date'] = pd.to_datetime(store_data['opening_date'], errors ='coerce')
        store_data.loc[[31, 179, 248, 341, 375], 'staff_numbers'] = [78, 30, 80, 97, 39] # individually replaces values that have been inccorectly including text
        store_data['staff_numbers'] = pd.to_numeric(store_data['staff_numbers'], errors='coerce')
        store_data.dropna(subset=['staff_numbers'], axis=0, inplace=True)

        store_data['continent'] = store_data['continent'].str.replace('eeEurope', 'Europe').str.replace('eeAmerica', 'America')

        return store_data
    
    def convert_product_weights(self, weight):
        
        weight = str(weight).strip().lower()
        
        if 'kg' in weight:
            weight = weight.replace('kg', '')
            weight = float(weight)

        elif 'ml' in weight:
            weight = weight.replace('ml', '')
            weight = float(weight)/1000

        elif 'g' in weight:
            weight = weight.replace('g', '')
            weight = float(weight)/1000

        elif 'lb' in weight:
            weight = weight.replace('lb', '')
            weight = float(weight)*0.453591

        elif 'oz' in weight:
            weight = weight.replace('oz', '')
            weight = float(weight)*0.0283495
            
        return weight
    
    def clean_products_data(self, product_data):
        product_data.replace('NULL', np.NaN, inplace=True)
        product_data['date_added'] = pd.to_datetime(product_data['date_added'], errors='coerce')
        product_data.dropna(subset=['date_added'], how='any', axis=0, inplace=True)
        
        # Handle the weight column
        product_data['weight'] = product_data['weight'].apply(lambda x: x.replace(' .', '') if isinstance(x, str) else x)
        
        # Split weights that contain 'x'
        temp_cols = product_data.loc[product_data['weight'].str.contains('x', na=False), 'weight'].str.split('x', expand=True)
        numeric_cols = temp_cols.apply(lambda x: pd.to_numeric(x.str.extract('(\d+\.?\d*)', expand=False)), axis=1)
        final_weight = numeric_cols.prod(axis=1)
        product_data.loc[product_data['weight'].str.contains('x', na=False), 'weight'] = final_weight

        # Convert weights to kg
        product_data['weight'] = product_data['weight'].apply(self.convert_product_weights)
        product_data.drop(product_data.columns[0], axis=1, inplace=True) 
        return product_data