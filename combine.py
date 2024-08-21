from data_extraction import DataExtractor
from data_cleaning import DataCleaning
from database_utils import DatabaseConnector
import pandas as pd

def main():
    # Initialize the DatabaseConnector
    connector = DatabaseConnector()
    
    # Read the database credentials
    db_creds = connector.read_db_creds()
    
    # Initialize the database engine
    engine = connector.init_db_engine(db_creds)
    
    # Extract data from the 'legacy_users' table
    extractor = DataExtractor(connector)
    user_data_df = extractor.extract_user_data('legacy_users')
    
    # Clean the extracted user data
    cleaner = DataCleaning()
    cleaned_data_df = cleaner.clean_user_data(user_data_df)
    
    # Upload the cleaned data to the 'dim_users' table in the RDS database
    connector.upload_to_db(cleaned_data_df, 'dim_users', engine)

    # Extract the number of stores
    headers = {"x-api-key": "yFBQbwXe9J3sd6zWVAMrK6lcxxr0q1lr2PT6DDMX"}
    stores_endpoint = "https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/store_details"
    number_of_stores_endpoint = "https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/number_stores"
    num_stores = extractor.list_number_of_stores(number_of_stores_endpoint, headers)
    
    if num_stores:
        # Retrieve store data
        store_data_df = extractor.retrieve_stores_data(num_stores, stores_endpoint, headers)
        
        # Clean the store data
        cleaned_store_data_df = cleaner.clean_store_data(store_data_df)
        
        # Upload the cleaned store data to the 'dim_store_details' table in the RDS database
        connector.upload_to_db(cleaned_store_data_df, 'dim_store_details', engine)
    
    # Extract product data from S3
    s3_address = 's3://data-handling-public/products.csv'
    product_data_df = extractor.extract_from_s3(s3_address)
    
    # Clean the product data
    cleaned_product_data_df = cleaner.clean_products_data(product_data_df)
    
    # Upload the cleaned product data to the 'dim_products' table in the RDS database
    connector.upload_to_db(cleaned_product_data_df, 'dim_products', engine)

if __name__ == '__main__':
    main()