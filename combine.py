from data_extraction import DataExtractor
from data_cleaning import DataCleaning
from database_utils import DatabaseConnector

def main():
    # Initialize the DatabaseConnector with the path to your YAML file
    connector = DatabaseConnector('db_creds.yaml')
    
    # Extract data from the 'legacy_users' table
    extractor = DataExtractor(connector)
    user_data_df = extractor.extract_user_data('legacy_users')
    
    # Clean the extracted user data
    cleaner = DataCleaning()
    cleaned_data_df = cleaner.clean_user_data(user_data_df)
    
    # Upload the cleaned data to the 'dim_users' table in the 'sales_data' database
    connector.upload_to_db(cleaned_data_df, 'dim_users', connector.read_db_creds())
    
if __name__ == '__main__':
    main()