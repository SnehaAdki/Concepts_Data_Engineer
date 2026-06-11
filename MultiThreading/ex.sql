insert into CORE.FLAGS 


select 'f354cfa1-6c5b-4a71-a22c-557d78382a7b__c6e2c26c-c0f0-449a-9562-2553e07dac83__6a656cc8-d81b-48fc-9147-6d603f4ad19a' as STUDY_ENV_UUID_SNAPSHOT_UUID_PERCENTAGE_KRI_UUID, subj.subject_uuid as SUBJECT_UUID, 

NVL(num_qry.flag_value,False) as FLAG_VALUE, 
'Percent Missing Lab (Chemistry)' as NAME, 
subj.subject_id as SUBJECT_ID, '' as TIME_TO_LIVE, 
'f354cfa1-6c5b-4a71-a22c-557d78382a7b' as STUDY_ENV_UUID, 
'c6e2c26c-c0f0-449a-9562-2553e07dac83' as SNAPSHOT_UUID, NVL(dem_qry.denominator_value,False) as DENOMINATOR_VALUE, 
CAST(CONVERT_TIMEZONE('UTC', CAST(CURRENT_TIMESTAMP() AS TIMESTAMP_TZ(9))) AS TIMESTAMP_NTZ(9)) as CREATED_AT, 
CAST(CONVERT_TIMEZONE('UTC', CAST(CURRENT_TIMESTAMP() AS TIMESTAMP_TZ(9))) AS TIMESTAMP_NTZ(9)) as UPDATED_AT, 
'6a656cc8-d81b-48fc-9147-6d603f4ad19a' as PERCENTAGE_KRI_UUID, 'active' as KRI_STATUS from (
    
    select distinct subject_id,subject_uuid from core.subjects where study_env_uuid='f354cfa1-6c5b-4a71-a22c-557d78382a7b' and snapshot_uuid = (
        select snapshot_uuid from core.snapshots where study_env_uuid='f354cfa1-6c5b-4a71-a22c-557d78382a7b' and source_of_data in ('FORMCLINICAL_INGESTOR', 'STREAM_SYNC', 'INGESTOR', 'SYNC', 'STREAM_INGESTOR', 'FORMCLINICAL_SYNC') order by created_at desc limit 1)) subj left join (select subject_uuid,subject_id, max( condition0) as flag_value from(select subject_uuid, subject_id, 
        iff(try_cast(PLANNED_EVENT_NAME::text as varchar) in  ('Withdrawal of Informed Consent'),True,False) as condition0 
        from   
        where study_environment_uuid='f354cfa1-6c5b-4a71-a22c-557d78382a7b' and snapshot_uuid='c6e2c26c-c0f0-449a-9562-2553e07dac83' and ITM_GRP_OID='DSG003' )x group by subject_uuid,subject_id) num_qry on subj.subject_uuid =num_qry.subject_uuid left join (
            select subject_uuid,subject_id, max( condition0 and condition1) as denominator_value from(
                select subject_uuid, subject_id, iff(try_cast(GET(form_fields, 'DSSCAT')::text as varchar) in  ('SCREENING DISPOSITION'),True,False) as condition0, iff(try_cast(GET(form_fields, 'DSDECOD')::text as varchar) in  ('COMPLETED'),True,False) as condition1 from  where study_environment_uuid='f354cfa1-6c5b-4a71-a22c-557d78382a7b' and snapshot_uuid='c6e2c26c-c0f0-449a-9562-2553e07dac83' and ITM_GRP_OID='DSH001' )x group by subject_uuid,subject_id) dem_qry on subj.subject_uuid =dem_qry.subject_uuid