-- Q3. Monthly revenue with a year-to-date running total and month-on-month growth.
-- Window functions: SUM(...) OVER for the YTD cumulative (partitioned by branch
-- and year so it resets each January), LAG for the prior month comparison.
WITH monthly AS (
    SELECT
        branch,
        YEAR(created_at)              AS "year",
        MONTH(created_at)             AS month_number,
        MONTHNAME(created_at)         AS monthname,
        ROUND(SUM(net_revenue), 2)    AS totalnetrevenue,
        COUNT(*)                      AS totalbookings
    FROM bookings
    GROUP BY 1, 2, 3, 4
)
SELECT
    branch                            AS "Location",
    "year"                            AS "Year",
    monthname,
    totalnetrevenue,
    totalbookings,
    ROUND(SUM(totalnetrevenue) OVER (
        PARTITION BY branch, "year"
        ORDER BY month_number
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2)  AS cumulativeyearlyrevenue,
    LAG(totalnetrevenue) OVER (
        PARTITION BY branch ORDER BY "year", month_number)     AS previousmonthrevenue,
    ROUND(100.0 * (totalnetrevenue - LAG(totalnetrevenue) OVER (
              PARTITION BY branch ORDER BY "year", month_number))
          / NULLIF(LAG(totalnetrevenue) OVER (
              PARTITION BY branch ORDER BY "year", month_number), 0), 2)  AS mom_growth_pct
FROM monthly
ORDER BY branch, "year", month_number;
