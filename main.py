from fastapi import FastAPI, Response, status, Query
import hashlib
import datetime
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
app.patient_id = 0
app.dane = list()


class PatientResp(BaseModel):
    id: Optional[int] = 0
    name: str
    surname: str
    register_date: Optional[str] = ""
    vaccination_date: Optional[str] = ""

@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.get("/method")
def get_method(response: Response):
    response.status_code = status.HTTP_200_OK
    return {"method": "GET"}


@app.options("/method")
def options_method(response: Response):
    response.status_code = status.HTTP_200_OK
    return {"method": "OPTIONS"}


@app.put("/method")
def put_method(response: Response):
    response.status_code = status.HTTP_200_OK
    return {"method": "PUT"}


@app.delete("/method")
def delete_method(response: Response):
    response.status_code = status.HTTP_200_OK
    return {"method": "DELETE"}


@app.post("/method")
def post_method(response: Response):
    response.status_code = status.HTTP_201_CREATED
    return {"method": "POST"}


@app.get("/auth")
def chech_hash_password(response: Response, password: str = Query(""), password_hash: str = Query("")):
    if hashlib.sha512(bytes(password, 'ascii')).hexdigest() == password_hash and any(password):
        response.status_code = status.HTTP_204_NO_CONTENT
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED


@app.post("/register")
def patients(response: Response, patient_json: PatientResp):
    app.patient_id += 1
    register_date = datetime.datetime.today()
    patient_dict = patient_json.dict()
    patient_dict["id"] = app.patient_id
    patient_dict["register_date"] = register_date.strftime("%Y-%m-%d")
    patient_dict["vaccination_date"]=(register_date + datetime.timedelta(len(patient_dict["name"].replace(" ", "")) + len(patient_dict["surname"].replace(" ", "")))).strftime("%Y-%m-%d")
    response.status_code = status.HTTP_201_CREATED
    #app.dane.append({"id": patients_id, "dane": data})

    return patient_dict

@app.get("/patient/{pat_id}")
def patients_id(response: Response, pat_id: int = Query(None)):
    if pat_id < 1:
        response.status_code = status.HTTP_400_BAD_REQUEST
    elif pat_id > app.patient_id:
        response.status_code = status.HTTP_404_NOT_FOUND
    else:
        response.status_code = status.HTTP_200_OK
        return app.dane[pat_id][1]
