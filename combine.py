from data_extraction import DataExtractor
from data_cleaning import DataCleaning
from database_utils import DatabaseConnector

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
    
if __name__ == '__main__':
    main()
