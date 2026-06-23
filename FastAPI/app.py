from fastapi import FastAPI, Depends
from fastapi.params import Body
from FastAPI.utils.snowflake_connect import create_snowflake_connection ,create_snowflake_connection_sqlalchemy
from snowflake.connector.pandas_tools import pd_writer
import pandas as pd

app = FastAPI()


def get_engine_connection():
    connection = create_snowflake_connection()
    try:
        yield connection
    finally:
        print("Closing the connection")
        connection.close()

def get_engine_connection_sqlalcehmy():
    connection = create_snowflake_connection_sqlalchemy()
    try:
        yield connection
    finally:
        print("Closing the connection")
        # connection.close()


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
def create(body=Body(), snowflake_engin=Depends(get_engine_connection_sqlalcehmy)):
    generate_data = pd.DataFrame({
        "user_id": [int(body["USER_ID"])],
        "user_name": [body["USER_NAME"]],
        "age": [int(body["AGE"])],
    })
    generate_data.to_sql("users", con=snowflake_engin, if_exists="append", index=False)
    print("Inserted Record .... ")
    return {"body": body}

@app.delete("/{id}", status_code=200)
def delete(id: int, snowflake_engin=Depends(get_engine_connection)):
    print(f"Deleting record with ID: {id}")
    query = f"DELETE FROM users_model.users WHERE user_id = {id}"
    cursor = snowflake_engin.cursor()
    try:
        cursor.execute(query)
        snowflake_engin.commit()
        breakpoint()
        if cursor.rowcount == 0:
            print(f"No record found with ID: {id}.")

            raise Exception({"id": id, "message": "No record found to delete."})
        else:
            print(f"Record with ID: {id} deleted successfully.")
    except Exception as e:
        print(f"Error deleting record with ID: {id}. Error: {e}")
        return {"Exception": {"id": id, "message": "Error deleting record."} }
    finally:
        print("Closing Cursor")
        cursor.close()

    return {"id": id, "message": "Record deleted successfully.  "}


@app.put("/update/{id}", status_code=200)
def update(id: int, body=Body(), snowflake_engin=Depends(get_engine_connection)):
    print(f"Updating record with ID: {id}")
    query = f"UPDATE users_model.users SET {body} WHERE user_id = {id}"

    cursor = snowflake_engin.cursor()
    cursor.execute(query)
    snowflake_engin.commit()
    breakpoint()
    return {"id": id, "body": result}