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

        user_data_df['date_of_birth'] = pd.to_datetime(user_data_df['date_of_birth'], errors = 'ignore')
        user_data_df['join_date'] = pd.to_datetime(user_data_df['join_date'], errors ='coerce')
        user_data_df = user_data_df.dropna(subset=['join_date'])

        user_data_df['phone_number'] = user_data_df['phone_number'].str.replace('/W', '')
        user_data_df = user_data_df.drop_duplicates(subset=['email_address'])
        
        user_data_df.drop(user_data_df.columns[0], axis=1, inplace=True)
        user_data_df.to_csv("users.csv")
        return user_data_df 