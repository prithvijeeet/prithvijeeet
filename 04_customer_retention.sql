-- Q4. Customer retention by branch and product.
-- A "repeat guest" is a customer_id seen more than once at that branch.
-- Answers which products bring people back, not just which sell most.
WITH guest_visits AS (
    SELECT branch, item_name, customer_id, COUNT(*) AS visits
    FROM bookings
    GROUP BY 1, 2, 3
)
SELECT
    branch,
    item_name,
    COUNT(*)                                              AS total_unique_guests,
    COUNT(*) FILTER (WHERE visits > 1)                    AS repeat_guests_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE visits > 1) / NULLIF(COUNT(*), 0), 2)
                                                          AS customer_retention_rate_pct
FROM guest_visits
GROUP BY 1, 2
ORDER BY branch, customer_retention_rate_pct DESC;
