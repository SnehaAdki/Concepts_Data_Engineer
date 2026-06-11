{% snapshot snap_tags  %}
{{
    config(
        target_schema = 'snapshots',
        unique_key = ['user_id','movie_id','tags'],
        strategy = 'timestamp',
        updated_at = 'tag_timestamp',
        invalidate_hard_deletes =True
    )
}}

select 
{{ dbt_utils.generate_surrogate_key(['user_id','movie_id','tags']) }} as ROW_KEY,
    user_id , 
    movie_id,
    tags,
    CAST(timestamp AS timestamp_ntz) as tag_timestamp

FROM {{ref('src_tags')}}


{% endsnapshot %}