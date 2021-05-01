from fastapi import FastAPI, Response, status, Query, Request, HTTPException, Cookie, Header, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
import hashlib
from datetime import datetime, timedelta, date
from pydantic import BaseModel
from typing import Optional, Dict
from fastapi.templating import Jinja2Templates
import secrets
from random import randint


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
templates = Jinja2Templates(directory="templates")
security = HTTPBasic() #KUR** JEST 6 RANO A JA DOPIERO POMYSLALEM
                        # O PRZECZYTANIU DOKUMENTACJI NA TEMAT BASE AUTH W FAST API **UJ MI W *UPE!!!
app.l_token = []
app.s_token = []

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



app.last_login_session = []
app.last_login_token = []

import random
random.seed(datetime.datetime.now())

@app.post("/login_session", status_code=201)
def login_session(response: Response, credentials: HTTPBasicCredentials = Depends(
    security)):  # pobiera user i password za pomocą BasicAuth
    # return {"username": credentials.username, "password": credentials.password} # wydobywanie user i password
    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")
    if not (correct_password and correct_username):
        raise HTTPException(status_code=401)
    secret = str(random.randint(0, 999999))
    session_token = hashlib.sha256(f"{credentials.username}{credentials.password}{secret}".encode()).hexdigest()
    response.set_cookie(key="session_token", value=session_token)
    if len(app.last_login_session) >= 3:
        app.last_login_session.pop(0)
    app.last_login_session.append(session_token)
    return {"OK"}

@app.post("/login_token", status_code=201)
def login_token(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")
    if not (correct_password and correct_username):
        raise HTTPException(status_code=401)
    secret = str(random.randint(0, 999999))
    session_token = hashlib.sha256(f"{credentials.username}{credentials.password}{secret}".encode()).hexdigest()
    if len(app.last_login_token) >= 3:
        app.last_login_token.pop(0)
    app.last_login_token.append(session_token)
    return {"token": session_token}

# dostęp
from fastapi.responses import PlainTextResponse

@app.get("/welcome_session")
def welcome_session(format: str = "", session_token: str = Cookie(None)):
    if session_token not in app.last_login_session:
        raise HTTPException(status_code=401)
    if format == "json":
        return {"message": "Welcome!"}
    elif format == "html":
        return HTMLResponse(content="<h1>Welcome!</h1>", status_code=200)
    else:
        return PlainTextResponse(content="Welcome!", status_code=200)

@app.get("/welcome_token")
def welcome_token(token: str = "", format: str = ""):
    if (token == "") or (token not in app.last_login_token):
        raise HTTPException(status_code=401)
    if format == "json":
        return {"message": "Welcome!"}
    elif format == "html":
        return HTMLResponse(content="<h1>Welcome!</h1>", status_code=200)
    else:
        return PlainTextResponse(content="Welcome!", status_code=200)

# wylogowywanie
from fastapi.responses import RedirectResponse

@app.delete("/logout_session")
def logout_session(format: str = "", session_token: str = Cookie(None)):
    if session_token not in app.last_login_session:
        raise HTTPException(status_code=401)

    app.last_login_session.remove(session_token)
    url = "/logged_out?format=" + format
    return RedirectResponse(url=url, status_code=303)

@app.delete("/logout_token")
def logout_token(token: str = "", format: str = ""):
    if (token == "") or (token not in app.last_login_token):
        raise HTTPException(status_code=401)

    app.last_login_token.remove(token)
    url = "/logged_out?format=" + format
    return RedirectResponse(url=url, status_code=303)

@app.get("/logged_out", status_code=200)
def logged_out(format: str = ""):
    if format == "json":
        return {"message": "Logged out!"}
    elif format == "html":
        return HTMLResponse(content="<h1>Logged out!</h1>", status_code=200)
    else:
        return PlainTextResponse(content="Logged out!", status_code=200)