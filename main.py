from fastapi import FastAPI, Response, status, Query, Request, HTTPException
import hashlib
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional, Dict


class PatientResp(BaseModel):
    id: Optional[int]
    name: str
    surname: str
    register_date: Optional[str] = ""
    vaccination_date: Optional[str] = ""

    def __init__(self, **kwargs):
        super().__init__(
            register_date=datetime.now().date(),
            vaccination_date=datetime.now().date()
            + timedelta(days=PatientResp.vaccination_timedelta(kwargs.get("name"), kwargs.get("surname"))),
            **kwargs,
        )

    @classmethod
    def vaccination_timedelta(cls, name, surname):
        name_letters = "".join(filter(str.isalpha, name))
        surname_letters = "".join(filter(str.isalpha, surname))

        return len(name_letters) + len(surname_letters)


app = FastAPI()
app.count_id: int = 1
app.storage: Dict[int, PatientResp] = {}


@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.api_route(path="/method", methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"], status_code=200)
def dif_requests(requests: Request, response: Response):
    request_method = requests.method

    if request_method == "POST":
        response.status_code = status.HTTP_201_CREATED

    return {"method": request_method}


@app.get("/auth")
def chech_hash_password(response: Response, password: str = Query(""), password_hash: str = Query("")):
    if hashlib.sha512(bytes(password, 'ascii')).hexdigest() == password_hash and any(password):
        response.status_code = status.HTTP_204_NO_CONTENT
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED


@app.post("/register", status_code=201)
def patients(patientresp: PatientResp):
    patientresp.id = app.count_id
    app.storage[app.count_id] = patientresp
    app.count_id += 1
    return patientresp


@app.get("/patient/{pat_id}")
def patients_id(pat_id: int):
    if pat_id < 1:
        raise HTTPException(status_code=400, detail="Invalid patient id")

    if pat_id not in app.storage[pat_id]:
        raise HTTPException(status_code=404, detail="Invalid patient id")

    return app.storage.get(pat_id)
