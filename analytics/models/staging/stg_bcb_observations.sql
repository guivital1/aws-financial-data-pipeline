select
    cast(series_slug as varchar) as series_slug,
    cast(series_name as varchar) as series_name,
    cast(unit as varchar) as unit,
    cast(frequency as varchar) as frequency,
    cast(observation_date as date) as observation_date,
    cast(value as double) as value,
    cast(source as varchar) as source,
    cast(snapshot_generated_at as timestamp) as snapshot_generated_at
from {{ ref('bcb_observations') }}
