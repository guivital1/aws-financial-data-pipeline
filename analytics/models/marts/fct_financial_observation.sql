select
    md5(concat(s.series_slug, '|', cast(s.observation_date as varchar))) as observation_key,
    i.indicator_key,
    cast(strftime(s.observation_date, '%Y%m%d') as integer) as date_key,
    s.observation_date,
    s.value,
    s.snapshot_generated_at
from {{ ref('stg_bcb_observations') }} as s
join {{ ref('dim_indicator') }} as i using (series_slug)
