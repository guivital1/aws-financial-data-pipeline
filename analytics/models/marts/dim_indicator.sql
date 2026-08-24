select
    row_number() over (order by series_slug) as indicator_key,
    series_slug,
    max(series_name) as indicator_name,
    max(unit) as unit,
    max(frequency) as frequency,
    max(source) as source
from {{ ref('stg_bcb_observations') }}
group by series_slug
