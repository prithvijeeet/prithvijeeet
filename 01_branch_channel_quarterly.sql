-- Q1. Walk-in vs advance revenue, by branch and quarter.
-- Business question: is each site's revenue coming from planned visits or
-- from footfall, and is that mix changing over time?
SELECT
    branch,
    YEAR(session_at)                                        AS "year",
    'Q' || QUARTER(session_at)                              AS quarter,
    COUNT(*) FILTER (WHERE lead_time_days < 1)              AS walkin_bookings_count,
    COUNT(*) FILTER (WHERE lead_time_days >= 1)             AS advance_bookings_count,
    ROUND(SUM(net_revenue) FILTER (WHERE lead_time_days < 1), 2)   AS walkin_revenue,
    ROUND(SUM(net_revenue) FILTER (WHERE lead_time_days >= 1), 2)  AS advance_revenue
FROM bookings
WHERE lead_time_days IS NOT NULL
GROUP BY 1, 2, 3
ORDER BY branch, "year", quarter;
