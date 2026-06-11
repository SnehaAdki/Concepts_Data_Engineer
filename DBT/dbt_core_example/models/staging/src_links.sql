with 
raw_links as (
    -- select * from MOVIELENS.RAW.RAW_LINKS
    select * from {{ source('netflix', 'r_links') }}
)
select 
imdbid as imdb_id,
movieId as movie_id,
tmdbid as tmbd_id
from raw_links