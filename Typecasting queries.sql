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
	
-- Dim tables primary key / foreign key creation ----------------------------------

-- Adds primary keys in dim_tables
ALTER TABLE dim_card_details
	ADD CONSTRAINT pk_card_number PRIMARY KEY (card_number);

ALTER TABLE dim_date_times
	ADD PRIMARY KEY (date_uuid);
	
ALTER TABLE dim_products
	ADD PRIMARY KEY (product_code);
	
ALTER TABLE dim_store_details
	ADD PRIMARY KEY (store_code);
	
ALTER TABLE dim_users
	ADD PRIMARY KEY (user_uuid);
	
-- Finds all card_numbers in orders_table that are not in dim_card_details
SELECT orders_table.card_number 
FROM orders_table
LEFT JOIN dim_card_details
ON orders_table.card_number = dim_card_details.card_number
WHERE dim_card_details.card_number IS NULL;

-- Inserts all card_numbers from orders_tale not present in dim_card_details initally, into dim_card_details
INSERT INTO dim_card_details (card_number)
SELECT DISTINCT orders_table.card_number
FROM orders_table
WHERE orders_table.card_number NOT IN 
	(SELECT dim_card_details.card_number
	FROM dim_card_details);
	
-- Find the user_uuid values in orders_table that are missing in dim_users	
SELECT orders_table.user_uuid
FROM orders_table
LEFT JOIN dim_users
ON orders_table.user_uuid = dim_users.user_uuid
WHERE dim_users.user_uuid IS NULL;

-- Insert the missing user_uuid values from orders_table into dim_users
INSERT INTO dim_users (user_uuid)
SELECT DISTINCT orders_table.user_uuid
FROM orders_table
WHERE orders_table.user_uuid NOT IN 
    (SELECT dim_users.user_uuid
     FROM dim_users);

-- Find product code values missing from orders_table
SELECT orders_table.product_code
FROM orders_table
LEFT JOIN dim_products
ON orders_table.product_code = dim_products.product_code
WHERE dim_products.product_code IS NULL;

-- Insert missing product code values into dim_products
INSERT INTO dim_products (product_code)
SELECT DISTINCT orders_table.product_code
FROM orders_table
WHERE orders_table.product_code NOT IN 
    (SELECT product_code FROM dim_products);

	
-- Adds the foreign keys to the orders table
ALTER TABLE orders_table
	ADD CONSTRAINT fk_orders_card_number
	FOREIGN KEY (card_number)
	REFERENCES dim_card_details(card_number); -- come back to add this
	
ALTER TABLE orders_table
	ADD CONSTRAINT fk_orders_date_uuid
	FOREIGN KEY (date_uuid)
	REFERENCES dim_date_times(date_uuid);
	
ALTER TABLE orders_table
	ADD CONSTRAINT fk_orders_product_code
	FOREIGN KEY (product_code)
	REFERENCES dim_products(product_code);
	
ALTER TABLE orders_table
	ADD CONSTRAINT fk_orders_store_code
	FOREIGN KEY (store_code)
	REFERENCES dim_store_details(store_code);
	
ALTER TABLE orders_table
	ADD CONSTRAINT fk_orders_user_uuid
	FOREIGN KEY (user_uuid)
	REFERENCES dim_users(user_uuid);
	
-- All primary keys

SELECT
    kcu.table_name,
    kcu.column_name,
    tc.constraint_name
FROM
    information_schema.table_constraints AS tc
JOIN
    information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
WHERE
    tc.constraint_type = 'PRIMARY KEY'
    AND tc.table_schema = 'public'; 
	
-- All foreign keys

SELECT
    kcu.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    tc.constraint_name
FROM
    information_schema.table_constraints AS tc
JOIN
    information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN
    information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE
    tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'; 
	
-- Removing extra fks	

-- Locating all fks
SELECT conname
FROM pg_constraint
WHERE conrelid = 'orders_table'::regclass
  AND contype = 'f';
  
-- Erasing all extra fks
ALTER TABLE orders_table
	DROP CONSTRAINT orders_table_card_number_fkey,
	DROP CONSTRAINT orders_table_card_number_fkey1,
	DROP CONSTRAINT orders_table_card_number_fkey2;
	
ALTER TABLE orders_table
	DROP CONSTRAINT orders_table_date_uuid_fkey,
	DROP CONSTRAINT orders_table_date_uuid_fkey1,
	DROP CONSTRAINT orders_table_date_uuid_fkey2; -- date
	
ALTER TABLE orders_table
	DROP CONSTRAINT orders_table_user_uuid_fkey,
	DROP CONSTRAINT orders_table_user_uuid_fkey1,
	DROP CONSTRAINT orders_table_user_uuid_fkey2; -- user
	
ALTER TABLE orders_table
	DROP CONSTRAINT orders_table_store_code_fkey,
	DROP CONSTRAINT orders_table_store_code_fkey1;
	
ALTER TABLE orders_table
	DROP CONSTRAINT orders_table_product_code_fkey;

-- All the pk names
SELECT conname
FROM pg_constraint
WHERE conrelid = 'orders_table'::regclass
  AND contype = 'p'; 

-- All the fk names
SELECT conname
FROM pg_constraint
WHERE conrelid = 'orders_table'::regclass
  AND contype = 'f';
  



	