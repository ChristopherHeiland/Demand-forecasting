-- Rossmann Store Sales - exploratory SQL queries

-- Average sales by store type
SELECT
    st.StoreType,
    COUNT(*)                        AS n_days,
    ROUND(AVG(s.Sales), 0)          AS avg_daily_sales,
    ROUND(SUM(s.Sales) / 1000.0, 0) AS total_sales_thousands
FROM sales s
JOIN stores st ON s.Store = st.Store
GROUP BY st.StoreType
ORDER BY avg_daily_sales DESC;


-- Promo impact on sales and footfall
SELECT
    Promo,
    ROUND(AVG(Sales), 0) AS avg_sales,
    ROUND(AVG(Customers), 0) AS avg_customers
FROM sales
GROUP BY Promo;


-- Monthly sales trend
SELECT
    strftime('%Y-%m', Date) AS year_month,
    ROUND(SUM(Sales) / 1000.0, 0) AS total_sales_thousands
FROM sales
GROUP BY year_month
ORDER BY year_month;


-- Top 10 stores by total sales
SELECT *
FROM (
    SELECT
        Store,
        SUM(Sales) AS total_sales,
        RANK() OVER (ORDER BY SUM(Sales) DESC) AS sales_rank
    FROM sales
    GROUP BY Store
)
WHERE sales_rank <= 10;


-- Rolling 7-day average, Store 1
SELECT
    Date,
    Sales,
    ROUND(AVG(Sales) OVER (
        ORDER BY Date
        ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING
    ), 0) AS rolling_7day_avg
FROM sales
WHERE Store = 1
ORDER BY Date
LIMIT 30;


-- Sales vs. competition proximity
SELECT
    CASE
        WHEN st.CompetitionDistance < 1000 THEN '< 1km'
        WHEN st.CompetitionDistance < 5000 THEN '1-5km'
        ELSE '5km+'
    END AS competition_proximity,
    ROUND(AVG(s.Sales), 0) AS avg_daily_sales,
    COUNT(DISTINCT s.Store) AS n_stores
FROM sales s
JOIN stores st ON s.Store = st.Store
GROUP BY competition_proximity
ORDER BY avg_daily_sales DESC;
