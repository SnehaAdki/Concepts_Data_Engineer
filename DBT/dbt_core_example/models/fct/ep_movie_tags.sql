with fct_movie_tags as (
    select * from {{ ref('dim_movies_tags')}}
)
select * from fct_movie_tags