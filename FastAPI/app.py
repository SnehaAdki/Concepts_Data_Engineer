from typing import Annotated
from fastapi import FastAPI, Depends
from fastapi.params import Body
from FastAPI.utils.snowflake_connect import create_snowflake_connection

app = FastAPI()


def get_engine_connection():
    db_connection = None
    try:
        db_connection = create_snowflake_connection()
        yield db_connection
    finally:
        print("Closing the connection")
        db_connection.close()


engine_connection = Annotated[object, Depends(get_engine_connection)]

@app.get("/",status_code=200)
def read_root():
    return {"Hello": "World"}


@app.post("/",status_code=201)
def create( body = Body() , snowflake_engin : engine_connection = Depends(get_engine_connection)):
    print(body)
    return {"body": body}

@app.put("/",status_code=201)
def update( body = Body() , snowflake_engin : engine_connection = Depends(get_engine_connection)):
    print(body)
    return {"body": body}