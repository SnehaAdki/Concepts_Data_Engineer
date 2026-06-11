{{
    config(
        materialized = 'incremental',
        on_schema_change = 'fail'
    )
}}
with src_rating as (
    select * from {{ ref('src_rating')}}
)
select 
    user_id, 
    movie_id,
    rating,
    timestamp as rating_timestamp,
    CURRENT_TIMESTAMP as created_at
from src_rating
where rating is not null

{% if is_incremental() %}
    AND timestamp > (select MAX(rating_timestamp) from {{this}})
{% endif %}




