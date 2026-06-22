from fastapi import FastAPI, Depends
from fastapi.params import Body
from FastAPI.utils.snowflake_connect import create_snowflake_connection
import pandas as pd

app = FastAPI()


def get_engine_connection():
    connection = create_snowflake_connection()
    try:
        yield connection
    finally:
        print("Closing the connection")
        connection.close()


def fetch_table_rows(connection, query: str):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        cursor.close()

@app.get("/", status_code=200)
def read_root(snowflake_engin=Depends(get_engine_connection)):
    query = "select * from users_model.users"
    rows = fetch_table_rows(snowflake_engin, query)
    return {"user_details": rows}


@app.post("/", status_code=201)
def create(body=Body(), snowflake_engin=Depends(get_engine_connection)):
    generate_data = pd.DataFrame({
        "user_id": [body["USER_ID"]],
        "user_name": [body["USER_NAME"]],
        "age": [body["AGE"]],
    })
    breakpoint()
    generate_data.to_sql("users", con=snowflake_engin, if_exists="append", index=False)
    print("Inserted Record .... ")
    return {"body": body}


@app.put("/", status_code=201)
def update(body=Body(), snowflake_engin=Depends(get_engine_connection)):
    print(body)
    return {"body": body}