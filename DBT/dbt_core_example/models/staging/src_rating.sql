with 
raw_ratings as (
    -- select * from MOVIELENS.RAW.RAW_RATINGS
    select * from {{ source('netflix', 'r_ratings') }}
)
select 
userid as user_id,
movieId as movie_id,
rating,
to_timestamp_ltz(timestamp) as timestamp
from raw_ratings