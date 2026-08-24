with monthly as (
    select
        observation_date,
        max(case when series_slug = 'selic_monthly' then value end) as selic_monthly,
        max(case when series_slug = 'ipca' then value end) as ipca_monthly
    from {{ ref('stg_bcb_observations') }}
    where series_slug in ('selic_monthly', 'ipca')
    group by observation_date
)

select
    observation_date,
    selic_monthly,
    ipca_monthly,
    selic_monthly - ipca_monthly as approximate_real_interest_spread
from monthly
where selic_monthly is not null and ipca_monthly is not null
