from fastapi import FastAPI, Response, status, Query, Request, HTTPException, Cookie
from fastapi.responses import JSONResponse
import hashlib
from datetime import datetime, timedelta, date
from pydantic import BaseModel
from typing import Optional, Dict
from fastapi.templating import Jinja2Templates


class PatientResp(BaseModel):
    id: Optional[int]
    name: str
    surname: str
    register_date: Optional[date]
    vaccination_date: Optional[date]

    def __init__(self, **kwargs):
        super().__init__(
            register_date=datetime.now().date(),
            vaccination_date=datetime.now().date()
            + timedelta(days=PatientResp.vaccination_timedelta(kwargs.get("name"), kwargs.get("surname"))
                        ),
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
app.token = None
templates = Jinja2Templates(directory="templates")


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
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")


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

    if pat_id not in app.storage:
        raise HTTPException(status_code=404, detail="Patient not found")

    return app.storage.get(pat_id)


@app.get("/hello")
def hello_html(request: Request):
    return templates.TemplateResponse("hello.html.j2", {
        "request": request, "date": datetime.now().date()})


@app.post("/login_session")
def login_session(response: Response, username: str = "", password: str = ""):
    user = "4dm1n"
    pas = "NotSoSecurePa$$"

    if user == username and pas == password:
        session_token = hashlib.sha256(f"{username}{password}".encode()).hexdigest()
        response.set_cookie(key="session_token", value=session_token)
        response = JSONResponse(content=session_token)
        response.set_cookie(key="session_token", value=session_token)
        response.status_code = status.HTTP_201_CREATED
        return response
    else:
        response.delete_cookie(key="session_token", path="/login_session")
        raise HTTPException(status_code=401, detail="Wrong Passowrd or Username")


@app.post("/login_token")
def login_token(*, response: Response, username: str = "", password: str = ""):
    user = "4dm1n"
    pas = "NotSoSecurePa$$"

    if user == username and pas == password:
        response.status_code = status.HTTP_201_CREATED
        token = hashlib.sha256(f"{username}{password}".encode()).hexdigest()
        return {"token": f"{token}"}
    else:
        raise HTTPException(status_code=401, detail="Wrong Passowrd or Username")



# @app.get("/welcome_session")
#
# @app.get("/welcome_token")