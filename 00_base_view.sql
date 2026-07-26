-- ---------------------------------------------------------------------------
-- Base view. Every other query in this folder reads from `bookings`.
--
-- The single most important line here is the cancellation filter: it is what
-- reconciles these outputs to the source system exactly (2,135 bookings,
-- £180,081.98 net revenue). Without it the totals run £944.99 high.
--
-- `created_at`  = when the booking was MADE
-- `session_at`  = when the session RUNS
-- These are different questions and the queries below are deliberate about
-- which one they group on. Weekday/weekend patterns must use session_at:
-- customers book on weekdays and visit at weekends.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW bookings AS
SELECT
    "Customer_ID"                        AS customer_id,
    "Booking ID"                         AS booking_id,
    "Location"                           AS branch,
    "Item Type"                          AS item_type,
    "Item"                               AS item_name,
    "Pax"                                AS pax,
    "Net revenue"                        AS net_revenue,
    created_at,
    session_at,
    lead_time_days,
    booking_channel,
    CASE WHEN DAYOFWEEK(session_at) IN (5, 6, 0)
         THEN 'Weekend Peak (Fri-Sun)'
         ELSE 'Weekday Slump (Mon-Thu)'
    END                                  AS traffic_segment
FROM read_parquet('data/processed/bookings_clean.parquet')
WHERE NOT is_cancelled;
