-- Q2. Weekday vs weekend revenue split, by branch and quarter.
-- Grouped on session_at, not created_at: the question is when customers VISIT.
-- Grouping on booking date instead inverts the answer entirely.
SELECT
    branch,
    YEAR(session_at)                                                        AS "year",
    'Q' || QUARTER(session_at)                                              AS quarter,
    ROUND(SUM(net_revenue) FILTER (WHERE traffic_segment LIKE 'Weekday%'), 2) AS total_weekday_revenue,
    ROUND(SUM(net_revenue) FILTER (WHERE traffic_segment LIKE 'Weekend%'), 2) AS total_weekend_revenue,
    ROUND(100.0 * SUM(net_revenue) FILTER (WHERE traffic_segment LIKE 'Weekday%')
          / NULLIF(SUM(net_revenue), 0), 2)                                 AS weekday_contribution_percentage
FROM bookings
GROUP BY 1, 2, 3
ORDER BY branch, "year", quarter;
