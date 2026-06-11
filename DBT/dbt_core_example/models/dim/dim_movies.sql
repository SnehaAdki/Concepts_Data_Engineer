with 
src_movies as (
    select * from {{ ref('src_movies')}}
)
select 
movie_id,
INITCAP(TRIM(title)) as movie_title,
SPLIT(genres , '|') as GENRES_ARRAY,
genres
from src_movies