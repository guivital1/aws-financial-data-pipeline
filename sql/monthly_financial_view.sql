CREATE OR REPLACE VIEW financial_analytics.monthly_financial_indicators AS
SELECT
    observation_date,
    max(CASE WHEN series_slug = 'selic_monthly' THEN value END) AS selic_monthly_pct,
    max(CASE WHEN series_slug = 'ipca' THEN value END) AS ipca_monthly_pct,
    max(CASE WHEN series_slug = 'selic_monthly' THEN value END)
        - max(CASE WHEN series_slug = 'ipca' THEN value END) AS approximate_real_rate_pct
FROM financial_analytics.bcb_raw
WHERE series_slug IN ('selic_monthly', 'ipca')
GROUP BY observation_date;
