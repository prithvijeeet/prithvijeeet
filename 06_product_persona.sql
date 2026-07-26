-- Q6. Product mix by traffic segment, with each item type's share of its
-- segment's revenue (window function over the segment partition).
-- Shows that Party bookings are a weekend phenomenon and almost absent midweek -
-- a concrete gap to sell into.
SELECT
    branch,
    traffic_segment,
    item_type,
    COUNT(*)                        AS total_bookings_count,
    ROUND(SUM(net_revenue), 2)      AS total_net_revenue,
    ROUND(100.0 * SUM(net_revenue)
          / NULLIF(SUM(SUM(net_revenue)) OVER (PARTITION BY branch, traffic_segment), 0), 2)
                                    AS segment_revenue_contribution_pct
FROM bookings
GROUP BY 1, 2, 3
ORDER BY branch, traffic_segment, total_net_revenue DESC;
