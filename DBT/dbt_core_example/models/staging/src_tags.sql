with 
raw_tags as (
    -- select * from MOVIELENS.RAW.RAW_TAGS
    select * from {{ source('netflix', 'r_tags') }}
)
select 
userid as user_id,
movieId as movie_id,
tags,
to_timestamp_ltz(timestamp) as tag_timestamp
from raw_tags