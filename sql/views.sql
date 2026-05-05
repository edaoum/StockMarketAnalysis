-- Daily return percentage for each ticker
CREATE OR REPLACE VIEW STOCK_ANALYTICS.ANALYTICS.V_DAILY_RETURNS AS
SELECT
    date,
    ticker,
    close_price,
    LAG(close_price) OVER (PARTITION BY ticker ORDER BY date) AS prev_close,
    ROUND(
        (close_price - LAG(close_price) OVER (PARTITION BY ticker ORDER BY date))
        / LAG(close_price) OVER (PARTITION BY ticker ORDER BY date) * 100
    , 4) AS daily_return_pct
FROM STOCK_ANALYTICS.RAW.STOCK_PRICES;



-- 30-day rolling volatility (standard deviation of daily returns)
CREATE OR REPLACE VIEW STOCK_ANALYTICS.ANALYTICS.V_VOLATILITY AS
SELECT
    date,
    ticker,
    close_price,
    daily_return_pct,
    ROUND(
        STDDEV(daily_return_pct) OVER (
            PARTITION BY ticker
            ORDER BY date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        )
    , 4) AS volatility_30d
FROM STOCK_ANALYTICS.ANALYTICS.V_DAILY_RETURNS
WHERE daily_return_pct IS NOT NULL;



-- Cumulative performance since 2020-01-01 (base 100)
CREATE OR REPLACE VIEW STOCK_ANALYTICS.ANALYTICS.V_CUMULATIVE_PERFORMANCE AS
SELECT
    date,
    ticker,
    close_price,
    FIRST_VALUE(close_price) OVER (
        PARTITION BY ticker ORDER BY date
    ) AS base_price,
    ROUND(close_price / FIRST_VALUE(close_price) OVER (
        PARTITION BY ticker ORDER BY date
    ) * 100, 2) AS indexed_price
FROM STOCK_ANALYTICS.RAW.STOCK_PRICES;



-- Join daily returns with macro indicators (monthly granularity)
CREATE OR REPLACE VIEW STOCK_ANALYTICS.ANALYTICS.V_MARKET_MACRO AS
SELECT
    r.date,
    r.ticker,
    r.daily_return_pct,
    r.volatility_30d,
    cpi.value   AS inflation,
    fed.value   AS fed_rate,
    unemp.value AS unemployment
FROM STOCK_ANALYTICS.ANALYTICS.V_VOLATILITY r
LEFT JOIN STOCK_ANALYTICS.RAW.MACRO_INDICATORS cpi
    ON DATE_TRUNC('month', r.date) = DATE_TRUNC('month', cpi.date)
    AND cpi.indicator = 'CPI'
LEFT JOIN STOCK_ANALYTICS.RAW.MACRO_INDICATORS fed
    ON DATE_TRUNC('month', r.date) = DATE_TRUNC('month', fed.date)
    AND fed.indicator = 'FEDFUNDS'
LEFT JOIN STOCK_ANALYTICS.RAW.MACRO_INDICATORS unemp
    ON DATE_TRUNC('month', r.date) = DATE_TRUNC('month', unemp.date)
    AND unemp.indicator = 'UNRATE';



-- Verify all views were created
SHOW VIEWS IN SCHEMA STOCK_ANALYTICS.ANALYTICS;

-- Quick sanity check on each view
SELECT * FROM STOCK_ANALYTICS.ANALYTICS.V_DAILY_RETURNS LIMIT 5;
SELECT * FROM STOCK_ANALYTICS.ANALYTICS.V_VOLATILITY LIMIT 5;
SELECT * FROM STOCK_ANALYTICS.ANALYTICS.V_CUMULATIVE_PERFORMANCE LIMIT 5;
SELECT * FROM STOCK_ANALYTICS.ANALYTICS.V_MARKET_MACRO LIMIT 5;