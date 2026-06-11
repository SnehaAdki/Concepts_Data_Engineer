with 
ratings as (
    select distinct user_id from {{ ref('src_rating')}}
),
tags as (
    select distinct user_id from {{ ref('src_tags')}}
)

select distinct user_id from 
(
    select * from ratings 
    union 
    select * from tags 
)
