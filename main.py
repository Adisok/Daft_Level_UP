from fastapi import FastAPI, Response, status, Query
import hashlib
import datetime

app = FastAPI()
app.patient_id = 0


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
    if hashlib.sha512(bytes(password, 'ascii')).hexdigest() == password_hash and any(password) :
        response.status_code = status.HTTP_204_NO_CONTENT
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED


@app.post("/register")
def patients(response: Response, name: str = Query(None), surname: str = Query(None)):
    app.patient_id += 1
    register_date = datetime.datetime.today()
    data = {
        "id": app.patient_id,
        "name": name,
        "surname": surname,
        "register_date": register_date.strftime("%Y-%m-%d"),
        "vaccination_date": (register_date + datetime.timedelta(len(name)+len(surname))).strftime("%Y-%m-%d")
    }
    response.status_code = status.HTTP_201_CREATED
    return data
