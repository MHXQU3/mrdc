# Multinational Retail Data Centralisation

This project was set by AICore and it implements an ETL (Extract, Transform, Load) pipeline which is designed to extract data from various sources,  clean the data, and load it into a PostgreSQL database. This project also involves designing a star-shaped schema for the aforementioned database before querying the data based on several scenarios provided for us.

## Scenario

You work for a multinational company that sells various goods across the globe.\
Currently, their sales data is spread across many different data sources making it not easily accessible or analysable by current members of the team.\
In an effort to become more data-driven, your organisation would like to make its sales data accessible from one centralised location.\
Your first goal will be to produce a system that stores the current company data in a database so that it's accessed from one centralised location and acts as a single source of truth for sales data.\
You will then query the database to get up-to-date metrics for the business.

## Table of Contents

- [Data Sources](#data-sources)
- [Data Cleaning](#data-cleaning)
- [Database Schema](#database-schema)
- [Typecasting The Tables](#typecasting-the-tables)
- [How to Run](#how-to-run)
- [Requirements](#requirements)
- [License](#license)



## Data Sources

- **User Data**: The historical data of users which is currently stored in an AWS database in the cloud.
- **Card Data**: Users card details which are stored in a PDF file in an AWS S3 bucket
- **Store Data**: Fetched from an API, with two GET methods, one endpoint providing the store count and the other providing store details.
- **Product Data**: The information for each product the company sells which is available as a CSV file in an S3 bucket.
- **Order Data**: The single source of truth for all orders the company has made in the past, which is stored in a database on AWS RDS.
- **Date Data**: A JSON file containing the details of when each sale happened, as well as related attributes, stored on S3.

## Data Cleaning

Data extracted from various sources is processed and cleaned to ensure consistency across tables. Below is the information on how each was carried out:
_Note: Comments were removed in the code segments of this `README.md` file to ensure conciseness and remove congestion. For comments please refer to the respective code files._

- **User Data**:
    - Handles `NULL` values.
    - Standardizes date formats.
    - Removes duplicate entries based on email addresses.
    - Saved to users.csv

    ```py
        def clean_user_data(self, legacy_users_table):
            legacy_users_table.replace('NULL', np.nan, inplace=True)
            legacy_users_table.dropna(subset=['date_of_birth', 'email_address', 'user_uuid'], how='any', axis=0, inplace=True) 

            legacy_users_table['date_of_birth'] = pd.to_datetime(legacy_users_table['date_of_birth'], errors = 'coerce')
            legacy_users_table['join_date'] = pd.to_datetime(legacy_users_table['join_date'], errors ='coerce')
            legacy_users_table = legacy_users_table.dropna(subset=['join_date'])

            legacy_users_table.loc[:, 'phone_number'] = legacy_users_table['phone_number'].str.replace('/W', '')
            legacy_users_table = legacy_users_table.drop_duplicates(subset=['email_address'])
            
            legacy_users_table.drop(legacy_users_table.columns[0], axis=1, inplace=True)
            legacy_users_table.to_csv("users.csv")
            return legacy_users_table 
    ```

- **Card Data**:
    - Strips out non-numeric characters from card numbers.
    - Filters out invalid or corrupted card numbers.
    ```py
    def clean_card_data(self, card_data_table):
        card_data_table.replace('NULL', np.nan, inplace=True)
        card_data_table.dropna(subset=['card_number'], how='any', axis=0, inplace=True)
        card_data_table = card_data_table[~card_data_table['card_number'].str.contains('[a-zA-Z?]', na=False)]
        return card_data_table  
    ```

- **Store Data**:
    - Corrects continent names and staff number inconsistencies.
    - Converts date fields to standardized formats.
    ```py
    def clean_store_data(self, store_data):
        store_data = store_data.reset_index(drop=True) 
        store_data.replace('NULL', np.nan, inplace=True)
        store_data['opening_date'] = pd.to_datetime(store_data['opening_date'], errors ='coerce')'opening_date'
        store_data.loc[[31, 179, 248, 341, 375], 'staff_numbers'] = [78, 30, 80, 97, 39]
        store_data['staff_numbers'] = pd.to_numeric(store_data['staff_numbers'], errors='coerce')
        store_data.dropna(subset=['staff_numbers'], axis=0, inplace=True)

        store_data['continent'] = store_data['continent'].str.replace('eeEurope', 'Europe').str.replace('eeAmerica', 'America')

        return store_data  
    ```

- **Product Data**:
    - Converts product weights into kilograms (supports multiple units like `g`, `kg`, `lb`, `oz`).
    - Removes unnecessary columns and ensures no duplicate entries.
    - Handles `NULL` values.
    - Drops rows with necessary entries missing

    ```py
    def convert_product_data(self, x):

        if 'kg' in x:
            x = x.replace('kg', '')
            x = float(x)

        elif 'ml' in x:
            x = x.replace('ml', '')
            x = float(x)/1000

        elif 'g' in x:
            x = x.replace('g', '')
            x = float(x)/1000

        elif 'lb' in x:
            x = x.replace('lb', '')
            x = float(x)*0.453591

        elif 'oz' in x:
            x = x.replace('oz', '')
            x = float(x)*0.0283495
            
        return x

    def clean_product_data(self, data):
        
        data.replace('NULL', np.nan, inplace=True)
        data['date_added'] = pd.to_datetime(data['date_added'], errors ='coerce')
        data.dropna(subset=['date_added'], how='any', axis=0, inplace=True)
        data['weight'] = data['weight'].apply(lambda x: x.replace(' .', ''))

        temp_cols = data.loc[data.weight.str.contains('x'), 'weight'].str.split('x', expand=True)
        numeric_cols = temp_cols.apply(lambda x: pd.to_numeric(x.str.extract(r'(\d+\.?\d*)', expand=False).fillna(0)), axis=1)
        final_weight = numeric_cols.prod(axis=1)
        data.loc[data.weight.str.contains('x'), 'weight'] = final_weight

        data['weight'] = data['weight'].apply(lambda x: str(x).lower().strip())
        data['weight'] = data['weight'].apply(lambda x: self.convert_product_data(x))

        data.drop(data.columns[0], axis=1, inplace=True) 
        return data
    ```

- **Order Data**:
    - Drops unnecessary columns like `first_name`, `last_name`, and metadata columns.
    - Ensures no duplicates exist.

    ```py
    def clean_order_data(self, data):
        data.drop("level_0", axis=1, inplace=True) 
        data.drop("1", axis=1, inplace=True) 
        data.drop(data.columns[0], axis=1, inplace=True)
        data.drop('first_name', axis=1, inplace=True)
        data.drop('last_name', axis=1, inplace=True)
        return data
    ```

- **Date Data**:
    - Converts year, month, and day fields into a unified `date` field.
    - Ensures that only valid date entries are kept.

    ```py
    def clean_date_data(self, data):
        data['year'] = pd.to_numeric(data['year'], errors='coerce')
        data.dropna(subset=['year'], how='any', axis=0, inplace=True)
        return data
    ```

## Database Schema

The cleaned data is stored in a PostgreSQL database using a star-based schema. Here is a quick overview:

- **The Main Table**: `orders_table`
    - Contains the main transactional data for all sales.
  
- **Dimension Tables**:
    - `dim_users`: Stores user-related information.
    - `dim_products`: Stores product-related details.
    - `dim_store_details`: Contains store-specific information.
    - `dim_date_times`: Stores details related to the date and time of each transaction.

- **Primary Key Information**:
    - **Table:** dim_date_times
        - **Column Name:** date_uuid
        - **Constraint Name:** dim_date_times_pkey 

    - **Table:** dim_products
        - **Column Name:** product_code
        - **Constraint Name:** dim_products_pkey

    - **Table:** dim_store_details
        - **Column Name:** store_code
        - **Constraint Name:** dim_store_details_pkey

    - **Table:** dim_users
        - **Column Name:** user_uuid
        - **Constraint Name:** dim_users_pkey

    - **Table:** dim_card_details
        - **Column Name:** card_number
        - **Constraint Name:** pk_card_number

- **Foreign Key Information**
    - **Foreign Key 1**
        - **Table:** orders_table
        - **Column Name:** date_uuid
        - **References Table:** dim_date_times
        - **References Column:** date_uuid
        - **Constraint Name:** fk_orders_date_uuid

    - **Foreign Key 2**
        - **Table:** orders_table
        - **Column Name:** product_code
        - **References Table:** dim_products
        - **References Column:** product_code
        - **Constraint Name:** fk_orders_product_code

    - **Foreign Key 3**
        - **Table:** orders_table
        - **Column Name:** store_code
        - **References Table:** dim_store_details
        - **References Column:** store_code
        - **Constraint Name:** fk_orders_store_code

    - **Foreign Key 4**
        - **Table:** orders_table
        - **Column Name:** user_uuid
        - **References Table:** dim_users
        - **References Column:** user_uuid
        - **Constraint Name:** fk_orders_user_uuid

    - **Foreign Key 5**
        - **Table:** orders_table
        - **Column Name:** card_number
        - **References Table:** dim_card_details
        - **References Column:** card_number
        - **Constraint Name:** fk_orders_card_number

## Typecasting The Tables
This section focuses on developing the star-based schema of the database, starting off with ensuring that the columns are of the correct data types.
- **Orders_table**
    - The VARCHAR constraints were found for each column that required one and then a character limit was placed upon them
    - Columns were typecasted to their appropriate data types
    ```SQL
    ALTER TABLE orders_table
        ALTER COLUMN card_number TYPE VARCHAR(19),
        ALTER COLUMN store_code TYPE VARCHAR(12),
        ALTER COLUMN product_code TYPE VARCHAR(11),
        ALTER COLUMN date_uuid TYPE UUID USING CAST(date_uuid as UUID),
        ALTER COLUMN user_uuid TYPE UUID USING CAST(user_uuid as UUID),
        ALTER COLUMN product_quantity TYPE SMALLINT;
    ```
- **Dim_users**
    - The VARCHAR constraints were found for each column that required one and then a character limit was placed upon them
    - Columns were typecasted to their appropriate data types
    ```SQL
    ALTER TABLE dim_users
	ALTER COLUMN first_name TYPE VARCHAR(225), -- The max limit for VARCHAR
	ALTER COLUMN last_name TYPE VARCHAR(255),
	ALTER COLUMN date_of_birth TYPE DATE USING CAST(date_of_birth AS DATE),
	ALTER COLUMN join_date TYPE DATE USING CAST(join_date AS DATE),
	ALTER COLUMN user_uuid TYPE UUID USING CAST(user_uuid AS UUID),
	ALTER COLUMN country_code TYPE VARCHAR(3);
    ```
- **Dim_store_details**
    - The VARCHAR constraints were found for each column that required one and then a character limit was placed upon them
    - `N/A` values were updated to `NULL`
    ```sql
    UPDATE dim_store_details 
    SET address = NULL
    WHERE address = 'N/A';

    UPDATE dim_store_details 
    SET longitude = NULL
    WHERE longitude = 'N/A';

    UPDATE dim_store_details 
    SET locality = NULL
    WHERE locality = 'N/A';

    UPDATE dim_store_details 
    SET lat = NULL
    WHERE lat = 'N/A';

    UPDATE dim_store_details
    SET latitude = CONCAT(CAST(lat as FLOAT), CAST(latitude as FLOAT));
    ```
    - lat and level_0 columns were unnecessary so dropped
    ```sql
    ALTER TABLE dim_store_details
	DROP lat,
	DROP level_0;
    ```
    - Columns were typecasted to their appropriate data types
    ```sql
    ALTER TABLE dim_store_details
        ALTER COLUMN longitude TYPE FLOAT USING CAST(longitude AS FLOAT),
        ALTER COLUMN locality TYPE VARCHAR(255),
        ALTER COLUMN store_code TYPE VARCHAR(12),
        ALTER COLUMN staff_numbers TYPE SMALLINT,
        ALTER COLUMN opening_date TYPE DATE USING CAST(opening_date as DATE),
        ALTER COLUMN store_type TYPE VARCHAR(255),
        ALTER COLUMN country_code TYPE VARCHAR(2),
        ALTER COLUMN continent TYPE VARCHAR(255);
    ```
- **Dim_products**
    - The VARCHAR constraints were found for each column that required one and then a character limit was placed upon them
    - Pound signs were removed so column could be typecasted
    ```sql
    UPDATE dim_products
    SET product_price = REPLACE(product_price, '£', '');
    ```
    - A column where the weights were categorised was added
    ```sql 
    UPDATE dim_products
    SET weight_class =
        CASE 
            WHEN weight < 2.0 THEN 'Light'
            WHEN weight >= 2 
                AND weight < 40 THEN 'Mid_Sized'
            WHEN weight >= 40 
                AND weight <140 THEN 'Heavy'
            WHEN weight >= 140 THEN 'Truck_Required'
        END;
    ```
    - Columns were typecasted to their appropriate data types
    ```sql
    ALTER TABLE dim_products
        ALTER COLUMN product_price TYPE FLOAT USING CAST(product_price as FLOAT),
        ALTER COLUMN weight TYPE FLOAT USING CAST(weight as FLOAT),
        ALTER COLUMN product_code TYPE VARCHAR(11),
        ALTER COLUMN date_added TYPE DATE USING CAST(date_added as DATE),
        ALTER COLUMN uuid TYPE UUID USING CAST(uuid as UUID),
        ALTER COLUMN "EAN" TYPE VARCHAR(17),
        ALTER COLUMN weight_class TYPE VARCHAR(14),
        ALTER COLUMN still_available TYPE boolean USING (still_available ='Still_available');
    ```
- **Dim_date_times**
    - The VARCHAR constraints were found for each column that required one and then a character limit was placed upon them
    - Columns were typecasted to their appropriate data types
    ```sql
    ALTER TABLE dim_date_times
        ALTER COLUMN month TYPE VARCHAR(2),
        ALTER COLUMN year TYPE VARCHAR(4),
        ALTER COLUMN day TYPE VARCHAR(2),
        ALTER COLUMN time_period TYPE VARCHAR(10),
        ALTER COLUMN date_uuid TYPE UUID USING CAST(date_uuid as UUID);
    ```

- **Dim_card_details**
    - The VARCHAR constraints were found for each column that required one and then a character limit was placed upon them
    - Columns were typecasted to their appropriate data types
    ```sql
    ALTER TABLE dim_card_details
        ALTER COLUMN card_number TYPE VARCHAR(19),
        ALTER COLUMN expiry_date TYPE VARCHAR(5),
        ALTER COLUMN date_payment_confirmed TYPE DATE USING CAST(date_payment_confirmed as DATE);
    ```


## How to Run

1. **Database Setup**: 
- Initialise a new local database which meets the local database requirements set out in the second half of `db_creds.yaml`
- Name it sales_data
   
2. **Running The Code**: Execute the `data_cleaning.py` script.
- This part of the code is where the entire ETL process happens:

```py
if __name__ == "__main__":
    extractor = DataExtractor()
    connector = DatabaseConnector()
    cleaner = DataCleaning()

    db_creds = connector.read_db_creds()
    engine = connector.init_db_engine(db_creds)
    table_names = connector.list_db_tables(engine)
    legacy_users_table = extractor.read_rds_table(table_names, 'legacy_users', engine)
    clean_legacy_users_table = cleaner.clean_user_data(legacy_users_table)
    clean_legacy_users_table.to_csv('users.csv')
    connector.upload_to_db(clean_legacy_users_table, "dim_users", db_creds)

    card_data_table = extractor.retrieve_pdf_data('https://data-handling-public.s3.eu-west-1.amazonaws.com/card_details.pdf')
    card_data_table.to_csv('card_details.csv')
    clean_card_data_table = cleaner.clean_card_data(card_data_table)
    clean_card_data_table.to_csv('card_data.csv')
    connector.upload_to_db(clean_card_data_table, "dim_card_details", db_creds)


    api_key = {'x-api-key': 'yFBQbwXe9J3sd6zWVAMrK6lcxxr0q1lr2PT6DDMX'}
    number_stores_endpoint = 'https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/number_stores'
    retrieve_store_endpoint = 'https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/store_details/'
    number_stores = extractor.list_number_of_stores(number_stores_endpoint, api_key)
    store_data = extractor.retrieve_stores_data(number_stores, retrieve_store_endpoint, api_key)
    store_data.to_csv('store_outputs.csv')
    clean_store_data_table = cleaner.clean_store_data(store_data)
    clean_store_data_table.to_csv('store_outputs.csv')
    connector.upload_to_db(clean_store_data_table, "dim_store_details", db_creds)


    product_data = extractor.extract_from_s3('s3://data-handling-public/products.csv')
    cleaned_product_data = cleaner.clean_product_data(product_data)
    cleaned_product_data.to_csv('product.csv')
    connector.upload_to_db(cleaned_product_data, 'dim_products', db_creds)

    orders_table = extractor.read_rds_table(table_names, 'orders_table', engine)
    clean_orders_table = cleaner.clean_order_data(orders_table)
    clean_orders_table.to_csv('orders.csv')
    connector.upload_to_db(clean_orders_table, "orders_table", db_creds)

    date_data = extractor.extract_from_s3('https://data-handling-public.s3.eu-west-1.amazonaws.com/date_details.json')
    clean_date_data = cleaner.clean_date_data(date_data)
    clean_date_data.to_csv('date.csv')
    connector.upload_to_db(clean_date_data, "dim_date_times", db_creds)
```

This script will:
- Extract data from AWS RDS, S3, PDFs, and APIs.
- Clean the data to ensure consistency.
- Return out all the data as csv files
- Load the cleaned data into the appropriate tables in your PostgreSQL database.

## Requirements

- Can be found in `requirements.txt`

## License

This project is licensed under AICore
