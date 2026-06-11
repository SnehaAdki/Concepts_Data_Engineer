with 
raw_movies as (
    -- select * from MOVIELENS.RAW.RAW_MOVIES
    select * from {{ source('netflix', 'r_movies') }}
)
select 
    movieId as movie_id ,
    title,
    genres
from raw_movies