-- How many stores does the business have in each country?
SELECT country_code AS country, COUNT(DISTINCT(address)) AS total_no_stores
FROM dim_store_details
GROUP BY country_code
ORDER BY total_no_stores DESC;

-- Which locations currently have the most stores
SELECT locality, COUNT(DISTINCT(address)) AS total_no_stores FROM dim_store_details
GROUP BY locality
ORDER BY total_no_stores DESC;

-- Which month produced the most sales
SELECT ddt.month, ROUND(SUM(o.product_quantity * dp.product_price)::numeric, 2) AS total_sales 
FROM orders_table o
JOIN dim_products dp
ON o.product_code = dp.product_code
JOIN dim_date_times ddt
ON o.date_uuid = ddt.date_uuid
GROUP BY ddt.month
ORDER BY total_sales DESC;

-- Online vs Offline sales count
with agg_locations AS (
	SELECT CASE 
		WHEN dsd.store_type = 'Web Portal' THEN 'Web'
		ELSE 'Offline'
		END AS location, COUNT(o.index) AS numbers_of_sales, SUM(o.product_quantity) AS product_quantity_count FROM dim_store_details dsd
	JOIN orders_table o
	ON o.store_code = dsd.store_code
	GROUP BY location
)
SELECT 
    location,
    SUM(numbers_of_sales) AS total_sales,
    SUM(product_quantity_count) AS total_product_quantity
FROM agg_locations
GROUP BY location;

-- Percentage of sales through each store
with loc_sales AS (
    SELECT dsd.store_type, 
    	ROUND(SUM(o.product_quantity * dp.product_price)::numeric, 2) AS total_sales
    FROM dim_store_details dsd
    JOIN orders_table o
    ON o.store_code = dsd.store_code
    JOIN dim_products dp
    ON o.product_code = dp.product_code
    GROUP BY dsd.store_type
),
sum_sales AS (
    SELECT SUM(total_sales) AS overall_sales
    FROM loc_sales
)
SELECT 
    ls.store_type, 
    ls.total_sales, 
    ROUND((ls.total_sales / ss.overall_sales) * 100, 2) AS pct_of_total_sales
FROM loc_sales ls, sum_sales ss
ORDER BY ls.total_sales DESC;

-- Which month in each year produced the highest cost of sales
with y_m_sales AS (
	SELECT SUM(o.product_quantity * dp.product_price), ddt.year, ddt.month FROM orders_table o
	JOIN dim_products dp
	ON dp.product_code = o.product_code
	JOIN dim_date_times ddt
	ON ddt.date_uuid = o.date_uuid 
	GROUP BY ddt.year, ddt.month
)
SELECT ROUND(MAX(SUM)::numeric, 2) AS total_sales, year, month FROM y_m_sales
GROUP BY year, month
ORDER BY total_sales DESC;

-- Staff headcount
SELECT SUM(staff_numbers) AS total_staff_numbers, country_code
FROM dim_store_details
GROUP BY country_code
ORDER BY total_staff_numbers DESC;

-- Which German store type is selling the most
SELECT ROUND(SUM(o.product_quantity * dp.product_price)::numeric, 2) AS total_sales, dsd.store_type, MAX(dsd.country_code) AS country_code
FROM orders_table o
LEFT JOIN dim_store_details dsd 
ON o.store_code = dsd.store_code
LEFT JOIN dim_products dp
ON o.product_code = dp.product_code
WHERE dsd.country_code = 'DE'
GROUP BY dsd.store_type
ORDER BY total_sales DESC;

-- How quickly is the company making sales
WITH time_table AS (
    SELECT 
        EXTRACT(hour FROM CAST(timestamp AS time)) AS hour,
        EXTRACT(minute FROM CAST(timestamp AS time)) AS minutes,
        EXTRACT(second FROM CAST(timestamp AS time)) AS seconds,
        day,
        month,
        year,
        date_uuid
    FROM dim_date_times
),
timestamp_table AS (
    SELECT 
        MAKE_TIMESTAMP(
            CAST(tt.year AS int), 
            CAST(tt.month AS int), 
            CAST(tt.day AS int),
            CAST(tt.hour AS int),
            CAST(tt.minutes AS int),
            CAST(tt.seconds AS float)
        ) AS order_timestamp,
        tt.date_uuid,
        tt.year
    FROM time_table tt
),
time_stamp_diffs AS (
    SELECT 
        ts.year, 
        LEAD(ts.order_timestamp) OVER (ORDER BY ts.order_timestamp ASC) - ts.order_timestamp AS time_diff
    FROM orders_table o
    JOIN timestamp_table ts ON o.date_uuid = ts.date_uuid
),
year_time_diffs AS (
    SELECT 
        year, 
        AVG(time_diff) AS average_time_diff
    FROM time_stamp_diffs
    GROUP BY year
    ORDER BY average_time_diff DESC
)
SELECT 
    year, 
    CONCAT(
        'hours: ', EXTRACT(HOUR FROM average_time_diff), '  ',
        'minutes: ', EXTRACT(MINUTE FROM average_time_diff), '  ',
        'seconds: ', CAST(EXTRACT(SECOND FROM average_time_diff) AS int), '  ',
        'milliseconds: ', CAST(EXTRACT(MILLISECOND FROM average_time_diff) AS int)
    ) AS formatted_time_diff
FROM year_time_diffs;


