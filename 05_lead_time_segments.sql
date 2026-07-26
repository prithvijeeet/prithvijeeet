-- Q5. Booking horizon by traffic segment - the query that changed the project's
-- conclusion.
--
-- Counting bookings says same-day walk-ins dominate. Adding revenue to the same
-- grouping shows advance planners are worth ~3x per booking and contribute an
-- equal share of revenue from a third of the volume. Volume and value point in
-- opposite directions here, and only the value view should drive marketing spend.
SELECT
    branch,
    traffic_segment,
    CASE
        WHEN lead_time_days < 1  THEN '00 Same-Day Walk-in'
        WHEN lead_time_days < 2  THEN '01 Next-Day Planner'
        WHEN lead_time_days < 4  THEN '02 Short-term (2-3 days)'
        WHEN lead_time_days < 8  THEN '03 Weekly Planner (4-7 days)'
        WHEN lead_time_days < 15 THEN '04 Mid-term (1-2 weeks)'
        ELSE                          '05 Long-term (2+ weeks)'
    END                                    AS booking_horizon,
    COUNT(*)                               AS total_bookings_count,
    ROUND(SUM(net_revenue), 2)             AS total_net_revenue,
    ROUND(AVG(lead_time_days), 1)          AS average_lead_time_days,
    ROUND(SUM(net_revenue) / NULLIF(COUNT(*), 0), 2) AS revenue_per_booking
FROM bookings
WHERE lead_time_days IS NOT NULL
GROUP BY 1, 2, 3
ORDER BY branch, traffic_segment, booking_horizon;
