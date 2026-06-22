from snowflake.connector import connect


def create_snowflake_paramers():
    return{
        "account": "TDSRKPP-LR22208",
        "user": "SADKI",
        "password": "Sneha@123456789",
        # "authenticator": "externalbrowser",
        "role": "ACCOUNTADMIN",
        "warehouse": "COMPUTE_WH",
        "database": "fastapi",
        "schema": "users_model"
    }

def create_snowflake_connection():
    params = create_snowflake_paramers()
    connection = connect(**params)
    return connection


