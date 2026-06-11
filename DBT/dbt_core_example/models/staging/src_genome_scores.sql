with 
GENOME_SCORES as (
-- select * from MOVIELENS.RAW.RAW_GENOME_SCORES
select * from {{ source('netflix', 'r_genome_scores') }}
)
select 
movieid as movie_id,
tagid as tag_id,
relevance
from GENOME_SCORES