select distinct
    cast(strftime(observation_date, '%Y%m%d') as integer) as date_key,
    observation_date,
    year(observation_date) as year,
    quarter(observation_date) as quarter,
    month(observation_date) as month,
    monthname(observation_date) as month_name,
    day(observation_date) as day_of_month,
    dayofweek(observation_date) as day_of_week
from {{ ref('stg_bcb_observations') }}
