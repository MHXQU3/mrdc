-- Orders_table type casting -----------------------------------------

-- Retrieve the data type of all the columns
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'orders_table';

-- Permenantly casts the data typers in the table
ALTER TABLE orders_table
	ALTER COLUMN card_number TYPE VARCHAR(19),
	ALTER COLUMN store_code TYPE VARCHAR(12),
	ALTER COLUMN product_code TYPE VARCHAR(11),
	ALTER COLUMN date_uuid TYPE UUID USING CAST(date_uuid as UUID),
	ALTER COLUMN user_uuid TYPE UUID USING CAST(user_uuid as UUID),
	ALTER COLUMN product_quantity TYPE SMALLINT;
	
-- Dim_users type casting ---------------------------------------------------------

-- Retrieve the data type of all the columns
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'dim_users';
	
-- Permenantly casts the data typers in the table
ALTER TABLE dim_users
	ALTER COLUMN first_name TYPE VARCHAR(225),
	ALTER COLUMN last_name TYPE VARCHAR(255),
	ALTER COLUMN date_of_birth TYPE DATE USING CAST(date_of_birth AS DATE),
	ALTER COLUMN join_date TYPE DATE USING CAST(join_date AS DATE),
	ALTER COLUMN user_uuid TYPE UUID USING CAST(user_uuid AS UUID),
	ALTER COLUMN country_code TYPE VARCHAR(3);
	
-- Dim_store_details type casting -------------------------------------------------

-- Retrieve the data type of all the columns
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'dim_store_details';

-- Updates NA values to NULL
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

-- Drops unneeded columns
ALTER TABLE dim_store_details
	DROP lat,
	DROP level_0;
	
-- Casts data types permenantly
ALTER TABLE dim_store_details
	ALTER COLUMN longitude TYPE FLOAT USING CAST(longitude AS FLOAT),
	ALTER COLUMN locality TYPE VARCHAR(255),
	ALTER COLUMN store_code TYPE VARCHAR(12),
	ALTER COLUMN staff_numbers TYPE SMALLINT,
	ALTER COLUMN opening_date TYPE DATE USING CAST(opening_date as DATE),
	ALTER COLUMN store_type TYPE VARCHAR(255),
	ALTER COLUMN country_code TYPE VARCHAR(2),
	ALTER COLUMN continent TYPE VARCHAR(255);

-- Dim_products type casting ------------------------------------------------------

-- Retrieve the data type of all the columns
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'dim_products';

-- Removes the pound sign in the product price column
UPDATE dim_products
SET product_price = REPLACE(product_price, '£', '');

-- Alters the column to a float type
ALTER TABLE dim_products 
	ALTER COLUMN weight TYPE FLOAT USING CAST(weight as FLOAT),
	ADD COLUMN weight_class VARCHAR;
	
-- Adds text categories based on the weights of the products
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
	
-- Renames column in dim_products
ALTER TABLE dim_products 
	RENAME COLUMN removed to still_available;
	
-- Permenantly alters data types in the table
ALTER TABLE dim_products
	ALTER COLUMN product_price TYPE FLOAT USING CAST(product_price as FLOAT),
	ALTER COLUMN weight TYPE FLOAT USING CAST(weight as FLOAT),
	ALTER COLUMN product_code TYPE VARCHAR(11),
	ALTER COLUMN date_added TYPE DATE USING CAST(date_added as DATE),
	ALTER COLUMN uuid TYPE UUID USING CAST(uuid as UUID),
	ALTER COLUMN "EAN" TYPE VARCHAR(17),
	ALTER COLUMN weight_class TYPE VARCHAR(14),
	ALTER COLUMN still_available TYPE boolean USING (still_available ='Still_available');
	
-- Dim_date_times type casting -------------------------------------------------

-- Retrieve the data type of all the columns
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'dim_date_times';	

-- Permenantly alters data types in the table
ALTER TABLE dim_date_times
	ALTER COLUMN month TYPE VARCHAR(2),
	ALTER COLUMN year TYPE VARCHAR(4),
	ALTER COLUMN day TYPE VARCHAR(2),
	ALTER COLUMN time_period TYPE VARCHAR(10),
	ALTER COLUMN date_uuid TYPE UUID USING CAST(date_uuid as UUID);

-- Dim_card_details type casting -------------------------------------------------

-- Retrieve the data type of all the columns
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'dim_card_details';

-- Permenantly alters data types in the table
ALTER TABLE dim_card_details
	ALTER COLUMN card_number TYPE VARCHAR(19),
	ALTER COLUMN expiry_date TYPE VARCHAR(5),
	ALTER COLUMN date_payment_confirmed TYPE DATE USING CAST(date_payment_confirmed as DATE);
	
	