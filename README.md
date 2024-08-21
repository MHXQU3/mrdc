# Data Handling and ETL Pipeline

This project involves building an ETL (Extract, Transform, Load) pipeline to process and manage various datasets from multiple sources and load them into a PostgreSQL database. The pipeline extracts data from AWS RDS, PDFs, AWS S3, and JSON files, cleans the data, and uploads it to the database.

## Project Structure

1. **Data Extraction**: Handles extraction of data from different sources.
2. **Data Cleaning**: Provides methods to clean and preprocess the data.
3. **Database Utilities**: Manages database connections and operations.
4. **Combiner Script**: Orchestrates the ETL process by coordinating extraction, cleaning, and loading.

## File Descriptions

### `db_creds.yaml`

This file stores all the database credentials needed for this project. Here you'll find both the RDS info and the local machine info.

```yaml
RDS_HOST: data-handling-project-readonly.cq2e8zno855e.eu-west-1.rds.amazonaws.com
RDS_PASSWORD: AiCore2022
RDS_USER: aicore_admin
RDS_DATABASE: postgres
RDS_PORT: 5432
RDS_DATABASE_TYPE: postgresql
DBAPI: psycopg2


LOCAL_DATABASE_TYPE: postgresql 
LOCAL_DB_API: psycopg2           
LOCAL_USER: postgres        
LOCAL_PASSWORD: password     
LOCAL_HOST: localhost            
LOCAL_PORT: 5432                 
LOCAL_DATABASE: sales_data      
```

### `data_extraction.py`

Contains the `DataExtractor` class for extracting data from various sources:
- **AWS RDS**: Extracts data from RDS tables.
- **PDF Files**: Retrieves data from PDFs using the `tabula` library.
- **AWS S3**: Handles data extraction from CSV, JSON files, and other file types in S3 buckets.
- **API Endpoints**: Retrieves data from REST APIs.

Example usage:
```python
from data_extraction import DataExtractor
from database_utils import DatabaseConnector

connector = DatabaseConnector()
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
```

### `data_cleaning.py`

Contains the 'DataCleaning' class with methods to clean and preprocess data. This class includes functionality for:

- **Cleaning User Data**: Handles data such as removing 'NULL' values, parsing dates, and formatting phone numbers. It also removes duplicates based on email addresses and drops unnecessary columns.
  
- **Cleaning Card Data**: Processes card data by handling 'NULL' values, sanitizing card numbers (removing non-numeric characters), and filtering out any invalid card numbers.

- **Cleaning Store Data**: Prepares store data by correcting specific values (e.g., replacing text with correct numbers), converting dates, and standardizing continent names.

- **Cleaning Product Data**: Deals with product weights by converting them to kilograms, handles missing values, and drops unnecessary columns.

- **Cleaning Order Data**: Removes unnecessary columns from the order data to ensure that only relevant information remains.

- **Cleaning Date Data**: Ensures that the year column is numeric, drops rows with missing year values, and removes columns with all missing values.

#### Example Usage

```py
from data_cleaning import DataCleaning

cleaner = DataCleaning()

# Clean user data
cleaned_user_data_df = cleaner.clean_user_data(user_data_df)
print(cleaned_user_data_df.head())

# Clean card data
cleaned_card_data_df = cleaner.clean_card_data(card_data)
print(cleaned_card_data_df.head())

# Clean store data
cleaned_store_data_df = cleaner.clean_store_data(store_data_df)
print(cleaned_store_data_df.head())

# Clean product data
cleaned_product_data_df = cleaner.clean_products_data(product_data_df)
print(cleaned_product_data_df.head())

# Clean order data
cleaned_order_data_df = cleaner.clean_order_data(orders_df)
print(cleaned_order_data_df.head())

# Clean date data
cleaned_date_data_df = cleaner.clean_date_data(date_data_df)
print(cleaned_date_data_df.head())
```

### `database_utils.py`

Provides the DatabaseConnector class for managing database connections and operations:

- **Reading Credentials**: Reads database credentials from a YAML file.
- **Initializing Engine**: Creates and connects to a SQLAlchemy engine.
- **Listing Tables**: Lists tables in a given database.
- **Uploading Data**: Uploads data frames to a specified table in the database.

#### Example Usage
```py
from database_utils import DatabaseConnector

connector = DatabaseConnector()
db_creds = connector.read_db_creds()
engine = connector.init_db_engine(db_creds)
```

### `combine.py`

Orchestrates the ETL pipeline by integrating data extraction, cleaning, and loading:

- Extracts user data, cleans it, and uploads it to the dim_users table.
- Retrieves and cleans store data, uploading it to the dim_store_details table.
- Extracts and cleans product data, uploading it to the dim_products table.
- Extracts and cleans order data, uploading it to the orders_table.
- Extracts and cleans date data, uploading it to the dim_date_times table.

#### Example Usage

```py
from combiner import main

if __name__ == '__main__':
    main()
```

### Environmental Requirements
- Python 3.x
- pandas
- numpy
- sqlalchemy
- psycopg2
- tabula-py
- requests
- boto3
- pyyaml

Install them all by running this code line in your terminal

```bash
pip install pandas numpy sqlalchemy psycopg2-binary tabula-py requests boto3 pyyaml
```

### Executing the pipeline

Run the following code in the terminal to execute the ETL pipeline:

```bash
python combine.py
```