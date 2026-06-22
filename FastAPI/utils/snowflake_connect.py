from snowflake.connector import connect
from sqlalchemy import create_engine


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

def create_snowflake_connection_sqlalchemy():
        # Create SQLAlchemy engine for pandas
    pswd = "Sneha@123456789"
    from snowflake.sqlalchemy import URL

    engine = create_engine(URL(
        account="TDSRKPP-LR22208",
        user="SADKI",
        password=pswd,
        database="FASTAPI",
        schema="USERS_MODEL",
        warehouse="COMPUTE_WH"
    ))
    return engine