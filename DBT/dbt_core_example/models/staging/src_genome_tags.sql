with 
RAW_GENOME_TAGS as (
    -- select * from MOVIELENS.RAW.RAW_GENOME_TAGS
    select * from {{ source('netflix', 'r_genome_tags') }}
)
select 
tagId as tag_id,
tag
from RAW_GENOME_TAGS