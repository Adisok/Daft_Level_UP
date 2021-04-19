from fastapi import FastAPI, Response, status, Query
from passlib.hash import sha512_crypt
import hashlib
import requests

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.get("/method")
def get_method(response: Response):
    response.status_code = status.HTTP_200_OK
    return {"method": "GET"}

@app.options("/method")
def get_method(response: Response):
    response.status_code = status.HTTP_200_OK
    return {"method": "OPTIONS"}

@app.put("/method")
def get_method(response: Response):
    response.status_code = status.HTTP_200_OK
    return {"method": "PUT"}

@app.delete("/method")
def get_method(response: Response):
    response.status_code = status.HTTP_200_OK
    return {"method": "DELETE"}

@app.post("/method")
def get_method(response: Response):
    response.status_code = status.HTTP_201_CREATED
    return {"method": "POST"}

@app.get("/auth")
def chech_hash_password(response: Response, password: str = Query(None), password_hash: str = Query(None)):
    if hashlib.sha512(bytes(password, 'ascii')).hexdigest() == password_hash:
        response.status_code = status.HTTP_204_NO_CONTENT
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
