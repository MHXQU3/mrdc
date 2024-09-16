from data_extraction import DataExtractor
from data_cleaning import DataCleaning
from database_utils import DatabaseConnector
import pandas as pd

def main():
    # Initialize the DatabaseConnector
    connector = DatabaseConnector('db_creds.yaml')
    # Read the database credentials
    db_creds = connector.read_db_creds()
    # Initialize the database engine
    engine = connector.init_db_engine()
    # Extract data from the 'legacy_users' table
    extractor = DataExtractor(connector)
    cleaner = DataCleaning()
    
    # Extract and clean user data
    user_data_df = extractor.extract_user_data('legacy_users')
    cleaned_data_df = cleaner.clean_user_data(user_data_df)
    connector.upload_to_db(cleaned_data_df, 'dim_users', db_creds)

    # Extract the number of stores
    headers = {"x-api-key": "yFBQbwXe9J3sd6zWVAMrK6lcxxr0q1lr2PT6DDMX"}
    stores_endpoint = "https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/store_details"
    number_of_stores_endpoint = "https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/number_stores"
    num_stores = extractor.list_number_of_stores(number_of_stores_endpoint, headers)
    
    if num_stores:
        store_data_df = extractor.retrieve_stores_data(num_stores, stores_endpoint, headers)
        cleaned_store_data_df = cleaner.clean_store_data(store_data_df)
        connector.upload_to_db(cleaned_store_data_df, 'dim_store_details', engine)
    
    # Extract and clean product data
    s3_address = 's3://data-handling-public/products.csv'
    product_data_df = extractor.extract_from_s3(s3_address)
    cleaned_product_data_df = cleaner.clean_products_data(product_data_df)
    connector.upload_to_db(cleaned_product_data_df, 'dim_products', engine)

    # Extract and clean order data
    orders_df = extractor.read_rds_table('orders_table')
    cleaned_orders_df = cleaner.clean_order_data(orders_df)
    connector.upload_to_db(cleaned_orders_df, 'orders_table', engine)

    # Extract and clean date data
    date_url = "https://data-handling-public.s3.eu-west-1.amazonaws.com/date_details.json"
    date_data_df = extractor.extract_from_s3(date_url)
    cleaned_date_data_df = cleaner.clean_date_data(date_data_df)
    connector.upload_to_db(cleaned_date_data_df, 'dim_date_times', engine)

if __name__ == '__main__':
    main()