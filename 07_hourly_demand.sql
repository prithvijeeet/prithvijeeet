-- Q7. Demand by day of week and hour of session - the staffing/scheduling view.
SELECT
    branch,
    DAYNAME(session_at)             AS day_of_week,
    HOUR(session_at)                AS hour_of_day,
    DAYOFWEEK(session_at)           AS dow_sort,
    COUNT(*)                        AS total_bookings_count,
    ROUND(SUM(net_revenue), 2)      AS hourly_net_revenue
FROM bookings
WHERE session_at IS NOT NULL
GROUP BY 1, 2, 3, 4
ORDER BY branch, dow_sort, hour_of_day;
