import os # pylint: disable=too-many-lines
import sys
import datetime
import time
import uuid
import multiprocessing as mp
import ijson.backends.yajl2_c as ijson
from src.awsutils import open_s3_file_stream, FormClinicalFiles, get_s3_file_size_in_gb
from src.batch_utils import handle_job_failure, get_blinded_form_oids, get_ttl_expiration_time
from src.snowflake_utils import  write_to_snowflake_datasets,meddrawhodrug_metadata_to_parquet
from utils.logging import setup_logger, create_extra, add_log_data, logger

S3_BLIND_CONFIG_BUCKET = os.environ.get('S3_BLIND_CONFIG_BUCKET','medsapi')
S3_BLIND_CONFIG_BUCKET_FOLDER= os.environ.get('S3_BLIND_CONFIG_BUCKET_FOLDER','sandbox/csa_extracts/')
S3_BLIND_CONFIG_STUDY_FORM_PATH=os.environ.get('S3_BLIND_CONFIG_STUDY_FORM_PATH','/config/blinded_forms.json')

LOG_LIMIT = int(os.environ.get('LOG_LIMIT', 500))
DATASET_WORKER_WRITERS_HIGH = int(
    os.environ.get('DATASET_WORKER_WRITERS_HIGH', 5))
DATASET_WORKER_WRITERS_LOW = int(
    os.environ.get('DATASET_WORKER_WRITERS_LOW', 1))
DATASET_FILE_SIZE_THRESHOLD_GB = float(
    os.environ.get('DATASET_FILE_SIZE_THRESHOLD_GB', 1.0))
DATASET_WORKER_QUEUE_MAX_SIZE = int(
    os.environ.get('DATASET_WORKER_QUEUE_MAX_SIZE', 500))
DATASET_WORKER_MIN_BUF_SIZE = int(
    os.environ.get(
        'DATASET_WORKER_MIN_BUF_SIZE',
        1000))
STAGE_NAME = os.environ.get('STAGE_NAME', 'sandbox')
MODULE_NAME = 'datasets'

class DatasetImporter: # pylint: disable=too-many-public-methods
    _snapshot_uuid = os.environ['SNAPSHOT_ID']
    _ttl_time = get_ttl_expiration_time()

    def __init__(self):
        self._row_count = 0
        self._log_row_count = 0

    def get_row_count(self):
        return self._row_count

    def _debug_log_to_limit(self, log_message, data):
        if self._log_row_count < LOG_LIMIT:
            self._log_row_count += 1
            logger.debug(log_message, extra=create_extra('row_data', data))

    @staticmethod
    def float_parse(itm):
        """
        Parse the Float Variables
        Parameter:
            itm :Sub dictionary of Clinical data
        """
        itm_dict = {
            itm['item_def_oid']: itm['value_N'],
            itm['item_def_oid'] +
            "_RAW": itm['value_S'] if itm['value_S'] else None,
        }
        if itm['codelist_decoded'] is not None:
            itm_dict[itm['item_def_oid'] + "_TXT"] = itm['codelist_decoded']
        if itm['standard_value_S'] is not None:
            itm_dict[itm['item_def_oid'] +
                     "_STD_RAW"] = itm['standard_value_S']
        if itm['standard_value_N'] is not None:
            itm_dict[itm['item_def_oid'] + "_STD"] = itm['standard_value_N']
        if itm['original_unit'] is not None:
            itm_dict[itm['item_def_oid'] + "_UNIT"] = itm['original_unit']
        if itm['standard_unit'] is not None:
            itm_dict[itm['item_def_oid'] + "_UNIT_STD"] = itm['standard_unit']
        return itm_dict

    @staticmethod
    def update_float_parse(itm):
        """
        Parse the Float Variables
        Parameter:
            itm :Sub dictionary of Clinical data
        """
        itm_dict = {
            itm['item_def_oid']:
                { "FLOAT" : float(itm['value_N']) if itm['value_N'] is not None else None,
                "SOURCE": str(itm['value_S']) if itm['value_S'] is not None else None,
                "CODELIST_DECODED" : str(itm['codelist_decoded']) if itm['codelist_decoded'] is not None else None,
                "STANDARDIZED_FLOAT_STRING" :
                    str(itm['standard_value_S']) if itm['standard_value_S'] is not None else None,
                "STANDARDIZED_FLOAT" : float(itm['standard_value_N']) if itm['standard_value_N'] is not None else None,
                'UNIT' : str(itm['original_unit']) if itm['original_unit'] is not None else None,
                'STANDARD_UNIT': str(itm['standard_unit']) if itm['standard_unit'] is not None else None,
                'UUID': str(itm['uuid'])
            }
        }
        return itm_dict

    @staticmethod
    def integer_parse(itm):
        """
        Parse the Integer Variables
        Parameter:
            itm :Sub dictionary of Clinical data
        Filter the fields in itm dictionary
        """
        itm_dict = {
            itm['item_def_oid']: itm['value_N'],
            itm['item_def_oid'] +
            "_RAW": itm['value_S'] if itm['value_S'] else None,
        }
        if itm['codelist_decoded'] is not None:
            itm_dict[itm['item_def_oid'] + "_TXT"] = itm['codelist_decoded']
        if itm['standard_value_S'] is not None:
            itm_dict[itm['item_def_oid'] +
                     "_STD_RAW"] = itm['standard_value_S']
        if itm['standard_value_N'] is not None:
            itm_dict[itm['item_def_oid'] + "_STD"] = itm['standard_value_N']
        if itm['original_unit'] is not None:
            itm_dict[itm['item_def_oid'] + "_UNIT"] = itm['original_unit']
        if itm['standard_unit'] is not None:
            itm_dict[itm['item_def_oid'] + "_UNIT_STD"] = itm['standard_unit']
        return itm_dict

    @staticmethod
    def update_integer_parse(itm):
        """
        Parse the Integer Variables
        Parameter:
            itm :Sub dictionary of Clinical data
        Filter the fields in itm dictionary
        """
        itm_dict = {
            itm['item_def_oid']: { "INTEGER" : int(itm['value_N']) if itm['value_N'] is not None else None,
                "SOURCE": str(itm['value_S']) if itm['value_S'] is not None else None,
                "CODELIST_DECODED" :
                    str(itm['codelist_decoded']) if itm['codelist_decoded'] is not None else None,
                "STANDARDIZED_INTEGER_STRING" :
                    str(itm['standard_value_S']) if itm['standard_value_S'] is not None else None,
                "STANDARDIZED_INTEGER" : int(itm['standard_value_N']) if itm['standard_value_N'] is not None else None,
                'UNIT' : str(itm['original_unit']) if itm['original_unit'] is not None else None,
                'STANDARD_UNIT': str(itm['standard_unit']) if itm['standard_unit'] is not None else None,
                'UUID': str(itm['uuid'])
            }
        }
        return itm_dict


    @staticmethod
    def parse_dictionary_result(itm):
        parsed_dr = {}
        atc_mapping = {1:'ATC_1',3:'ATC_2',4:'ATC_3',5:'ATC_4',7:'ATC_5'}
        try:
            if ((itm.get('dictionary_results') is not None) and (itm.get('dictionary') is not None)):
                for dic_res in itm['dictionary_results']:
                    if dic_res.get('medDicClasLvlName') is not None:
                        dic_class_name = str(dic_res.get('medDicClasLvlName')).upper()
                        if dic_class_name=='ATC':
                            atc_class_name = atc_mapping.get(len(dic_res.get('resultKey')))
                            if atc_class_name is not None:
                                parsed_dr.update(
                                    {atc_class_name+'_ID': str(dic_res.get('resultKey'))}
                                    )
                                parsed_dr.update(
                                    {atc_class_name+'_NAME': str(dic_res.get('resultValue'))}
                                    )
                        else:
                            parsed_dr.update(
                                {dic_class_name+'_ID': str(dic_res.get('resultKey'))}
                                )
                            parsed_dr.update(
                                {dic_class_name+'_NAME': str(dic_res.get('resultValue'))}
                                )
            return parsed_dr
        except BaseException:  # pylint: disable=bare-except
            return parsed_dr

    @staticmethod
    def parse_meddra_whodrug_dictionary_result(itm):
        # pylint: disable=too-many-branches
        parsed_dr = {}
        atc_whodrug_mapping = {1:'ATC1',3:'ATC2',4:'ATC3',5:'ATC4',7:'ATC5'}
        try:
            if (itm.get('dictionary_results') is not None) and (itm.get('dictionary') is not None):
                dictionary = str(itm.get('dictionary')).upper()
                if dictionary in ['MEDDRA','WHODRUG-GLOBAL-B3']:
                    for dic_res in itm['dictionary_results']:
                        if dic_res.get('medDicClasLvlName') is not None:
                            dic_class_name = dic_res.get('medDicClasLvlName').upper()
                            if dic_class_name == 'ATC' and dictionary == 'WHODRUG-GLOBAL-B3':
                                atc_class_name = atc_whodrug_mapping.get(len(dic_res.get('resultKey')))
                                if atc_class_name is not None:
                                    parsed_dr.update(
                                        {itm['item_def_oid'] + '_' +
                                         atc_class_name : dic_res.get('resultValue')}
                                        )
                            else:
                                parsed_dr.update(
                                        {itm['item_def_oid'] + '_' +
                                         dic_class_name : dic_res.get('resultValue')}
                                        )
            return parsed_dr
        except BaseException as ex:  # pylint: disable=bare-except
            logger.exception(
                'Error processing MedDRA/WHODrug dictionary mapping',
                extra=create_extra('err', ex))
            raise ex

    @staticmethod
    def string_parse(itm):
        """
        Parse the String Variables
        Parameter:
            itm :Sub dictionary of Clinical data
        """
        if itm['preferred_term'] is not None:
            if itm['codelist_decoded'] is None:
                return {
                    itm['item_def_oid']: itm['value_S'] if itm['value_S'] else None,
                    itm['item_def_oid'] +
                    '_PT': itm['preferred_term']}
            return {
                itm['item_def_oid']: itm['value_S'] if itm['value_S'] else None,
                itm['item_def_oid'] +
                '_TXT': itm['codelist_decoded'],
                itm['item_def_oid'] +
                '_PT': itm['preferred_term']}
        if itm['codelist_decoded'] is None:
            return {itm['item_def_oid']: itm['value_S']
                    if itm['value_S'] else None, }
        return {
            itm['item_def_oid']: itm['value_S'] if itm['value_S'] else None,
            itm['item_def_oid'] + '_TXT': itm['codelist_decoded']
        }

    @staticmethod
    def update_string_parse(itm):
        return {
            itm['item_def_oid']:
                {'SOURCE' : str(itm['value_S']) if itm['value_S'] is not None else None
                ,'CODELIST_DECODED':
                    str(itm['codelist_decoded']) if itm['codelist_decoded'] is not None else None
                ,'UUID': str(itm['uuid'])
                ,'PREFERRED_TERM':str(itm['preferred_term']) if itm['preferred_term'] is not None else None
                                  }
        }

    @staticmethod
    def date_parse(itm):
        """
        Parse the Date/DATETIME Variables
        Parameter:
            itm :Sub dictionary of Clinical data
        Filter the fields in itm dictionary
        """
        return {
            itm['item_def_oid']: itm['value_S'] if itm['value_S'] else None,
            itm['item_def_oid'] +
            "_DT": itm['value_DT'] if itm['value_DT'] else None,
            itm['item_def_oid'] +
            "_DTC": itm['value_DTC'] if itm['value_DTC'] else None,
            itm['item_def_oid'] +
            "_INT": itm['value_DTI'] if itm['value_DTI'] else None}

    @staticmethod
    def update_date_parse(itm):
        """
        Parse the Date/DATETIME Variables
        Parameter:
            itm :Sub dictionary of Clinical data
        Filter the fields in itm dictionary
        """
        return {
            itm['item_def_oid']: {
                "SOURCE" : str(itm['value_S']) if itm['value_S'] else None,
                "DATETIME_DT": str(itm['value_DT']) if itm['value_DT'] else None,
                "DATETIME_ISO": str(itm['value_DTC']) if itm['value_DTC'] else None,
                "DATETIME_IMPUTED": str(itm['value_DTI']) if itm['value_DTI'] else None,
                'UUID': str(itm['uuid'])
                    }
            }


    @staticmethod
    def boolean_parse(itm):
        """
        Parse the Boolean Variables
        Parameter:
            itm :Sub dictionary of Clinical data
        """
        return {
            itm['item_def_oid']: itm['value_N'],
            itm['item_def_oid'] +
            "_RAW": itm['value_S'] if itm['value_S'] else None}

    @staticmethod
    def update_boolean_parse(itm):
        """
        Parse the Boolean Variables
        Parameter:
            itm :Sub dictionary of Clinical data
        """
        return {
            itm['item_def_oid']: { 'BOOLEAN' : int(itm['value_N']) if itm['value_N'] is not None else None,
                                    "SOURCE": str(itm['value_S']) if itm['value_S'] is not None else None,
                                    "UUID": str(itm['uuid'])
                        }
            }

    @staticmethod
    def time_parse(itm):
        """
        Parse the Time Variables
        Parameter:
            itm :Sub dictionary of Clinical data
        """
        return {
            itm['item_def_oid']: itm['value_S'] if itm['value_S'] else None,
            itm['item_def_oid'] +
            "_DTC": itm['value_DTC'] if itm['value_DTC'] else None}

    @staticmethod
    def update_time_parse(itm):
        """
        Parse the Time Variables
        Parameter:
            itm :Sub dictionary of Clinical data
        """
        return {
            itm['item_def_oid']: { 'SOURCE': str(itm['value_S']) if itm['value_S'] else None,
                                    "DATETIME_ISO": str(itm['value_DTC']) if itm['value_DTC'] else None,
                                    'UUID': str(itm['uuid'])
                }
            }

    @staticmethod
    def string_and_dic_parse(itm):
        fields = {}
        string_variables = DatasetImporter.update_string_parse(itm)
        dic_variables = DatasetImporter.parse_dictionary_result(itm)

        if string_variables.get(itm['item_def_oid']) is not None:
            try:
                string_variables.get(itm['item_def_oid']).update(dic_variables)
            except BaseException:
                pass

        dict_updated_who_drug_medra = DatasetImporter.parse_new_meddra_whodrug(itm)
        fields.update(string_variables)
        if ((itm.get('dictionary_results') is not None) and (itm.get('dictionary') is not None)):
            fields.update(dict_updated_who_drug_medra)
        return fields

    @staticmethod
    def parse_new_meddra_whodrug(itm):
        parsed_dr = {}
        atc_mapping = {1:'ATC1',3:'ATC2',4:'ATC3',5:'ATC4',7:'ATC5'}
        try:
            if ((itm.get('dictionary_results') is not None) and (itm.get('dictionary') is not None)):
                for dic_res in itm['dictionary_results']:
                    if dic_res.get('medDicClasLvlName') is not None:
                        dic_class_name = str(dic_res.get('medDicClasLvlName')).upper()
                        if dic_class_name=='ATC':
                            atc_class_name = atc_mapping.get(len(dic_res.get('resultKey')))
                            if atc_class_name is not None:
                                parsed_dr.update(
                                    {
                                        f"{itm['item_def_oid']}_{atc_class_name}" : 
                                        {
                                            "SOURCE" : str(dic_res.get('resultValue')),
                                            "UUID" : itm['uuid']
                                        }
                                    })
                        else:
                            parsed_dr.update(
                            {
                                f"{itm['item_def_oid']}_{dic_class_name}":
                                {
                                    "SOURCE" : dic_res['resultValue'],
                                    "UUID" : itm['uuid']
                                }
                            })
            return parsed_dr
        except BaseException:  # pylint: disable=bare-except
            return parsed_dr


    @staticmethod
    def generate_meddrawhodrug_metadata(meddra_whodrug_variables):
        meddra_whodrug_metadata = []
        meddra_whodrug_unique_keys=list(set(meddra_whodrug_variables))
        for var_name in meddra_whodrug_unique_keys:
            meddra_whodrug_metadata.append(
                {
                'variable_name': var_name,
                'variable_oid': var_name,
                'data_type': 'STRING',
                'sas_label': var_name,
                'common_flag': False,
                'generated_variable': True,
                'visible': True
                }
                )
        return meddra_whodrug_metadata

    def add_variables(self, itm_data): # pylint: disable-msg=too-many-statements
        """
        Parse the variables from itm_data and add them to the fields dict
        Returns a dict of unique variable info for metadata variables
        Parameter:
            fields :dict of fields
            itm_data :array of variable data from Form Clinical
        Return: fields dict
        """
        fields = {}
        updated_fields = {}
        meddra_whodrug_variables= []
        for itm in itm_data:
            if not itm['item_def_uuid']:
                continue
            if itm['data_type'] == 'STRING':
                variables = DatasetImporter.string_parse(itm)
                updated_variables = DatasetImporter.string_and_dic_parse(itm)
                self._debug_log_to_limit('STRING data type', variables)
                self._debug_log_to_limit('UPDATED STRING data type', updated_variables)
                fields.update(variables)
                updated_fields.update(updated_variables)
            elif itm['data_type'] == 'DATE':
                variables = DatasetImporter.date_parse(itm)
                updated_variables = DatasetImporter.update_date_parse(itm)
                self._debug_log_to_limit('DATE data type', variables)
                self._debug_log_to_limit('UPDATED DATE data type', updated_variables)
                fields.update(variables)
                updated_fields.update(updated_variables)
            elif itm['data_type'] == 'DATETIME':
                variables = DatasetImporter.date_parse(itm)
                updated_variables = DatasetImporter.update_date_parse(itm)
                self._debug_log_to_limit('DATETIME data type', variables)
                self._debug_log_to_limit('UPDATED DATE data type', updated_variables)
                fields.update(variables)
                updated_fields.update(updated_variables)
            elif itm['data_type'] == 'INTEGER':
                variables = DatasetImporter.integer_parse(itm)
                updated_variables = DatasetImporter.update_integer_parse(itm)
                self._debug_log_to_limit('INTEGER data type', variables)
                self._debug_log_to_limit('UPDATED INTEGER data type', updated_variables)
                fields.update(variables)
                updated_fields.update(updated_variables)
            elif itm['data_type'] == 'BOOLEAN':
                variables = DatasetImporter.boolean_parse(itm)
                updated_variables = DatasetImporter.update_boolean_parse(itm)
                self._debug_log_to_limit('BOOLEAN data type', variables)
                self._debug_log_to_limit('UPDATED BOOLEAN data type', updated_variables)
                fields.update(variables)
                updated_fields.update(updated_variables)
            elif itm['data_type'] == 'FLOAT':
                variables = DatasetImporter.float_parse(itm)
                updated_variables = DatasetImporter.update_float_parse(itm)
                self._debug_log_to_limit('FLOAT data type', variables)
                self._debug_log_to_limit('UPDATED FLOAT data type', updated_variables)
                fields.update(variables)
                updated_fields.update(updated_variables)
            elif itm['data_type'] == 'TIME':
                variables = DatasetImporter.time_parse(itm)
                updated_variables = DatasetImporter.update_time_parse(itm)
                self._debug_log_to_limit('TIME data type', variables)
                self._debug_log_to_limit('TIME data type', updated_variables)
                fields.update(variables)
                updated_fields.update(updated_variables)
            else:
                logger.warning(
                    'Unknown data type', extra=create_extra(
                        'data_type', str(
                            itm['data_type'])))

            meddra_whodrug_dict_mapping = DatasetImporter.parse_meddra_whodrug_dictionary_result(itm)
            if len(meddra_whodrug_dict_mapping) > 0:
                fields.update(meddra_whodrug_dict_mapping)
                meddra_whodrug_variables+=list(meddra_whodrug_dict_mapping.keys())
        return fields, updated_fields, meddra_whodrug_variables

    @staticmethod
    def get_common_fields(subject, visit, clinical_data, parsed_metadata):
        """
        Parse fields that are common to all datasets
        Parameter:
            subject :subject information dict
            visit :single visit object from Form Clinical output
            clinical_data :array of clinical data from Form Clinical
            parsed_metadata : dict of information from file metadata
        Return: dict of fields
        """
        if os.environ.get('ROW_ID_RAND_ENABLED', 'false') == 'true':
            row_id = str(uuid.uuid4())
        else:
            row_id = clinical_data['itm_grp_data_uuid']
        return {
            'subject_uuid': subject['subject_uuid'].lower(),
            'SUBJECT_ID': subject['subject_identifier'],
            'PLANNED_EVENT_OID': visit['planned_event_oid'],
            'PLANNED_EVENT_NAME': visit['planned_event_name'],
            'PERFORMED_EVENT_NAME': visit['performed_event_name'],
            'PERFORMED_EVENT_DATE': visit['performed_event_date'],
            'ROW_ID': row_id,
            'METADATA_VERSION': subject['metadata_version'],
            'PERFORMED_EVENT_ORD_NUMBER': visit['performed_event_ord_number'],
            'ITM_GRP_REPEAT_KEY': clinical_data['itm_grp_repeat_key'],
            'ITM_GRP_OID': clinical_data['itm_grp_oid'],
            'ENVIRONMENT_OID': parsed_metadata['environment_oid'],
            'STUDY_NAME': parsed_metadata['study_name'],
            'CLIENT_DIVISION_NAME': parsed_metadata['client_division_name'],
            'time_to_live': DatasetImporter._ttl_time
        }

    @staticmethod
    def add_study_env_site_variables(
            fields,
            study_env_site_uuid,
            parsed_metadata):
        """
        adds the related fields from study_env_site wrt the uuid
        Parameter:
            fields (Dict): Contains all the common fields
            study_env_site_uuid (String): study_env_site_uuid value available at subject data
            parsed_metadata (Dict): dict of information from file metadata
        """
        study_env_site = parsed_metadata['study_env_site'][study_env_site_uuid]
        fields['SITE_NAME'] = study_env_site['site_name']
        fields['REGION_NAME'] = study_env_site['region_name']
        fields['COUNTRY_CODE_ALPHA3'] = study_env_site['country_code_alpha3']
        fields['STUDY_ENVIRONMENT_SITE_UUID'] = study_env_site['study_environment_site_uuid']
        fields['STUDY_ENVIRONMENT_COUNTRY_UUID'] = study_env_site['study_environment_country_uuid']
        fields['COUNTRY_UUID'] = study_env_site['country_uuid']

    @staticmethod
    def parse_metadata_stream(file_obj):
        """
        returns dict of metadata names/values.
        includes: study_environment_uuid
        Parameter:
            fileObject (IO Object): object of a file
        """
        logger.info('Parsing metadata')
        results = {}
        for key, val in ijson.kvitems(file_obj, ''):
            if key == 'metadata':
                results = val
                break
        results['study_env_site'] = {
            site_metadata['study_environment_site_uuid']: site_metadata
            for site_metadata in results['study_environment_site_metadata']
        }
        del results['study_environment_site_metadata']
        return results

    @staticmethod
    def add_ddb_primary_key(
            fields,
            clinical_data,
            study_environment_uuid,
            subject):
        """
        Add primary for dataset table in DDB
        Parameter:
            fields (Dict): dict of clinical data
            clinical_data (Dict): dict of clinical data
            study_environment_uuid (String): uuid
            subject (Dict): dict of Subject data
        """
        snapshot_id = DatasetImporter._snapshot_uuid
        fields['study_env_uuid_snapshot_uuid_dataset_oid_subject_uuid'] = study_environment_uuid \
            + '__' + snapshot_id + '__' \
            + clinical_data['form_oid'] + '__'\
            + subject['subject_uuid'].lower()
        return fields

    @staticmethod
    def add_ddb_sort_key(fields):
        """
        Add sort for dataset table in DDB
        Parameter:
            fields (Dict): dict of clinical data
        """
        fields['row_uuid'] = fields['ROW_ID']
        return fields

    @staticmethod
    def create_meta_dataset_format(study_environment_uuid, dataset_oids):
        """
        returns dict of variable metadata.
        Parameter:
            study_environment_uuid (String): study environment uuid from metadata
            dataset_oids (List): dataset list with form data
        """
        snapshot_id = DatasetImporter._snapshot_uuid
        parsed_format = {}
        for form in dataset_oids:
            form_format = {
                'study_env_uuid_snapshot_uuid': study_environment_uuid + '__' + snapshot_id,
                'dataset_oid': form,
                'dataset_name': None,
                'num_subject_uuids': 0,
                'unique_subject_uuids': set(),
                'num_rows': 0,
                'time_to_live': DatasetImporter._ttl_time}
            parsed_format[form] = form_format
        return parsed_format

    @staticmethod
    def update_dataset_metadata(dataset_meta, clinical_data, subject):
        """
        Adds data to dataset metadata dict.
        Parameter:
            dataset_meta (Dict): Dict with dataset metadata information
            clinical_data (Dict): dict of clinical data
            subject (Dict): dict of Subject data
            unique_var_info (Dict): dict of all the unique variables
        """
        form = dataset_meta[clinical_data['form_oid']]
        form['dataset_name'] = clinical_data['form_name']
        form['num_rows'] += 1
        form['unique_subject_uuids'].add(subject['subject_uuid'])


    @staticmethod
    def create_format_study_env(parsed_metadata):
        """
        returns dict of variable metadata and study env uuid.
        Parameter:
            file_obj_metadata (IO Object): object of a file
        """
        study_environment_uuid = parsed_metadata['study_environment_uuid']
        dataset_oids = parsed_metadata['forms_oids']
        dataset_metadata = DatasetImporter.create_meta_dataset_format(
            study_environment_uuid, dataset_oids)
        return dataset_metadata

    def _process_subject_data(
            self,
            *,
            subject,
            parsed_metadata,
            dataset_metadata):
        dataset_rows = []
        meddra_whodrug_variables = []
        max_last_updated_at = ''
        for visit in subject['visits']:
            for clinical_item in visit['clinical_data']:
                if clinical_item.get('itm_grp_data_uuid') is None:
                    logger.warning('Getting itm_grp_data_uuid null in form clinical file ',
                        extra=create_extra(['form_oid', 'subject_uuid'],
                            [clinical_item.get('form_oid'), subject.get('subject_uuid')]))
                    continue
                fields = self.get_common_fields(subject, visit, clinical_item,parsed_metadata)
                self.add_study_env_site_variables(fields, subject['study_environment_site_uuid'], parsed_metadata)
                if clinical_item['itm_data'] is None or len(clinical_item['itm_data']) == 0:
                    fields.update({})
                    fields["fields"] = {}
                else:
                    parse_data = self.add_variables(clinical_item['itm_data'])
                    fields.update(parse_data[0])
                    fields["fields"] = parse_data[1]
                    meddra_whodrug_variables+=parse_data[2]
                self.update_dataset_metadata(
                    dataset_metadata, clinical_item, subject)
                self.add_ddb_primary_key(
                    fields,
                    clinical_item,
                    parsed_metadata['study_environment_uuid'],
                    subject)
                self.add_ddb_sort_key(fields)
                self._row_count += 1
                dataset_rows.append(fields)
                if clinical_item['itm_data'] is not None and len(clinical_item['itm_data']) != 0:
                    for itm in clinical_item['itm_data']:
                        if 'last_updated_at' in itm and itm['last_updated_at']:
                            max_last_updated_at = max(
                                max_last_updated_at, itm['last_updated_at'])
                self._debug_log_to_limit('ROW data', fields)

        return dataset_rows, max_last_updated_at,meddra_whodrug_variables

    @staticmethod
    def _create_dataset_workers(
            ds_queue,
            log_config,
            dataset_worker_writers,
            unique_data_set,
            parsed_metadata):
        workers = []
        for i in range(dataset_worker_writers):
            worker = mp.Process(
                target=_dataset_writer_worker,
                args=(
                    ds_queue,
                    i,
                    log_config,
                    unique_data_set,
                    parsed_metadata))
            worker.start()
            workers.append(worker)
        return workers

    def s3_json_stream(self, file_obj, parsed_metadata,  # pylint: disable=too-many-arguments
                        log_config, dataset_worker_writers=1):
        # pylint: disable-msg=too-many-locals
        # pylint: disable=too-many-branches
        #pylint: disable=too-many-statements
        """
        Streams json data and logs first 5 rows.
        Parameter:
            fileObject (IO Object): object of a file
            fileObject_metadata (IO Object): object of a file
            log_config: logger configuration
        """
        manager = mp.Manager()
        unique_data_set = manager.list()  # shared variable within all workers
        if dataset_worker_writers > 0:
            ds_queue = mp.Queue(maxsize=DATASET_WORKER_QUEUE_MAX_SIZE)
            workers = self._create_dataset_workers(
                ds_queue,
                log_config,
                dataset_worker_writers,
                unique_data_set, parsed_metadata)
        else:
            ds_queue = None
            workers = ()
        dataset_metadata = self.create_format_study_env(parsed_metadata)
        dataset_rows = []
        meddra_whodrug_variables=[]
        logger.info('Iterating through the dataset file')
        dataset_start = datetime.datetime.now()
        max_last_updated_at = ''
        snapshot_uuid = self._snapshot_uuid
        study_environment_uuid = parsed_metadata["study_environment_uuid"]
        forms_oids = parsed_metadata['forms_oids'][0]
        timestamp = round(time.time() * 1000) # Kept timestamp for uniq filename in parquet

        try:
            logger.info('In batch ')
            for subject in ijson.items(file_obj, 'subjects_data.item'):
                cur_rows, cur_max_last_updated,meddra_whodrug_variables_temp = self._process_subject_data(
                    subject=subject, parsed_metadata=parsed_metadata,
                    dataset_metadata=dataset_metadata)
                max_last_updated_at = max(
                    max_last_updated_at, cur_max_last_updated)
                dataset_rows += cur_rows
                if dataset_worker_writers > 0:
                    if len(dataset_rows) >= DATASET_WORKER_MIN_BUF_SIZE:
                        ds_queue.put(dataset_rows)
                        dataset_rows = []
                else:
                    write_to_snowflake_datasets(
                        dataset_rows, unique_data_set, study_environment_uuid,
                        snapshot_uuid, MODULE_NAME, forms_oids, timestamp)
                    dataset_rows = []
                meddra_whodrug_variables += meddra_whodrug_variables_temp
            logger.info('Time taken for parsing data file', extra=create_extra(
                'time_taken', (datetime.datetime.now() - dataset_start).seconds))
        except BaseException as err:
            logger.exception('dataset importer failed', extra=create_extra(
                'error', str(err)))
            raise
        finally:
            close_sub_process(dataset_worker_writers,dataset_rows,ds_queue,workers)
        logger.info("Dataset Import Summary", extra=create_extra(
            ['row_count', 'DATASET_WORKER_WRITERS', 'max_last_updated_at'],
            [str(self._row_count), str(dataset_worker_writers), max_last_updated_at]))
        if  meddra_whodrug_variables:
            meddra_whodrug_dict={}
            #Generating Meddra WHodrug metadata
            meddra_whodrug_metadata=DatasetImporter.generate_meddrawhodrug_metadata(meddra_whodrug_variables)
            meddra_whodrug_dict['study_environment_uuid']=study_environment_uuid
            meddra_whodrug_dict['snapshot_id']=snapshot_uuid
            meddra_whodrug_dict['dataset_oid']=forms_oids
            meddra_whodrug_dict['var']=meddra_whodrug_metadata
            #Exporting Meddra WHodrug metadata in parquet
            meddrawhodrug_metadata_to_parquet(study_environment_uuid,forms_oids,snapshot_uuid,meddra_whodrug_dict)

def close_sub_process(dataset_worker_writers,dataset_rows,ds_queue,workers):
    if dataset_worker_writers > 0:
        if len(dataset_rows) > 0:
            ds_queue.put(dataset_rows)
        for _ in range(dataset_worker_writers):
            ds_queue.put(None)  # signal that we are done
        for worker in workers:
            worker.join()
        for worker in workers:  # check if any process failed
            if worker.exitcode != 0:
                logger.info(
                    "Worker exited with code ",
                    extra=create_extra(
                        'exitCode',
                        worker.exitcode))
                raise mp.ProcessError(
                    'One or More Dataset Worker Processes Failed (see logs).')


def _dataset_writer_worker(
        ds_queue,
        worker_num,
        log_config,
        unique_data_set,
        parsed_metadata):
    # pylint: disable-msg=too-many-locals
    setup_logger(data_dict=log_config, service_type='batch_process')
    add_log_data({'worker_num': worker_num})
    logger.info('Worker started')
    num_rows_written = 0
    while True:
        try:
            dataset_rows = ds_queue.get()
            if dataset_rows is None:
                logger.info('Worker exiting.',
                                extra=create_extra(['row_count'],
                                                [num_rows_written]))
                return
            logger.info('Worker writing rows')

            study_environment_uuid = parsed_metadata["study_environment_uuid"]
            snapshot_uuid = os.environ['SNAPSHOT_ID']
            forms_oids = parsed_metadata['forms_oids'][0]
            timestamp = round(time.time() * 1000) # Kept timestamp for uniq filename in parquet
            write_to_snowflake_datasets(
                dataset_rows, unique_data_set, study_environment_uuid,
                snapshot_uuid, MODULE_NAME, forms_oids, timestamp)

            num_rows_written += len(dataset_rows)
            logger.info(f"Worker wrote rows in {MODULE_NAME}",
                                extra=create_extra(['dataset_rows_length'],
                                                [len(dataset_rows)]))
        except BaseException as bex:  # pylint: disable=broad-except
            logger.exception(
                'Error processing item',
                extra=create_extra('err', bex))
            raise bex


def setup_log_data(s3_path, dataset_workers):
    data_dict = {
        'file_name': s3_path,
        'study_environment_uuid': os.getenv('STUDY_ENVIRONMENT_UUID'),
        'snapshot_uuid': os.getenv('SNAPSHOT_ID'),
        'ROW_ID_RAND_ENABLED': os.environ.get('ROW_ID_RAND_ENABLED', 'false'),
        'DATASET_WORKER_WRITERS': dataset_workers,
        'source': 'form_clinical',
        'step': 'dataset_importer'
    }
    if 'AWS_BATCH_JOB_ARRAY_INDEX' in os.environ:
        data_dict['job_array_index'] = os.environ['AWS_BATCH_JOB_ARRAY_INDEX']

    setup_logger(data_dict=data_dict, service_type='batch_process')
    return data_dict


@handle_job_failure
def main():
    # pylint: disable-msg=too-many-locals
    # pylint: disable-msg=too-many-statements
    job_run_id = int(os.environ["JOB_RUN_ID"])
    form_files_obj = FormClinicalFiles(s3_url=os.environ['S3_PATH'])
    s3_list = form_files_obj.data_files()
    if 'AWS_BATCH_JOB_ARRAY_INDEX' in os.environ:
        s3_path = s3_list[int(os.environ['AWS_BATCH_JOB_ARRAY_INDEX'])]
    else:
        s3_path = s3_list[0]
    dataset_workers = DATASET_WORKER_WRITERS_HIGH \
        if get_s3_file_size_in_gb(s3_path) >= DATASET_FILE_SIZE_THRESHOLD_GB \
        else DATASET_WORKER_WRITERS_LOW
    log_config = setup_log_data(s3_path, dataset_workers)
    logger.info('Beginning dataset import')
    start = datetime.datetime.now()
    data_import = DatasetImporter()
    if not s3_path.endswith('json'):
        logger.info("Completed dataset import - skipping non-json file",
                     extra=create_extra(['time_taken', 'row_count'],
                                        [(datetime.datetime.now() - start).seconds,
                                         data_import.get_row_count()]))
        return
    file_object_metadata = open_s3_file_stream(s3_path)
    parsed_metadata = data_import.parse_metadata_stream(file_object_metadata)
    study_environment_uuid = parsed_metadata["study_environment_uuid"]
    blind_form_config_file = "s3://" + S3_BLIND_CONFIG_BUCKET + "/" + S3_BLIND_CONFIG_BUCKET_FOLDER \
         + study_environment_uuid + S3_BLIND_CONFIG_STUDY_FORM_PATH
    blind_form_oids = get_blinded_form_oids(blind_form_config_file)
    exclude_form_oids = os.environ.get("FC_EXCLUDE_LIST", '').split(',')
    exclude_form_oids += blind_form_oids
    exclude_form_oids = [x for x in parsed_metadata['forms_oids'] if x in exclude_form_oids]
    if exclude_form_oids:
        logger.info("Completed dataset import - skipping the blinded file",
        extra=create_extra(['time_taken','study_environment_uuid','blinded_oid'],
        [(datetime.datetime.now() - start).seconds,study_environment_uuid,exclude_form_oids]))
        return
    try:
        file_object = open_s3_file_stream(s3_path)
        try:
            data_import.s3_json_stream(
                file_object,
                parsed_metadata,
                log_config,
                dataset_workers)
            logger.info('Completed dataset import', extra=create_extra(
                ['time_taken', 'row_count', 'DATASET_WORKER_WRITERS'],
                [(datetime.datetime.now() - start).seconds,
                 data_import.get_row_count(), str(dataset_workers)]))
        except BaseException as err:
            err.importer_name = "Dataset"
            raise
        finally:
            if file_object:
                file_object.close()
    except BaseException as err:
        err.importer_name = "Dataset"
        err.job_run_id = job_run_id
        raise
    finally:
        if file_object_metadata:
            file_object_metadata.close()


if __name__ == '__main__':
    sys.exit(main())