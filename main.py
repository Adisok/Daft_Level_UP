from fastapi import FastAPI, Response, status, Query, Request, HTTPException, Cookie, Header, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
import hashlib
from datetime import datetime, timedelta, date
from pydantic import BaseModel
from typing import Optional, Dict
from fastapi.templating import Jinja2Templates
import secrets



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
app.l_token = None
app.s_token = None

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
def login_session(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")

    if not (correct_password and correct_username):
        raise HTTPException(status_code=401, detail="Wrong Passowrd or Username")
    else:
        session_token = hashlib.sha256("4dm1n:NotSoSecurePa$$".encode()).hexdigest()
        response.set_cookie(key="session_token", value=f"{session_token}")
        response.status_code = status.HTTP_201_CREATED
        app.s_token = session_token
        return {"session_token": f"{session_token}"}

@app.post("/login_token")
def login_token(*, response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")

    if not (correct_password and correct_username):
        raise HTTPException(status_code=401, detail="Wrong Passowrd or Username")
    else:
        token = hashlib.sha256("4dm1n:NotSoSecurePa$$".encode()).hexdigest()
        response.status_code = status.HTTP_201_CREATED
        app.l_token = token
        return {"token": f"{token}"}


@app.get("/welcome_session", status_code=200)
def come_session(session_token: str = Cookie(None), format: Optional[str] = None):
    if session_token != app.s_token:
        raise HTTPException(status_code=401, detail="Wrong Passowrd or Username")
    else:
        if format == "json":
            return JSONResponse(content={"message": "Welcome!"})
        elif format == "html":
            return HTMLResponse(content="<h1>Welcome!</h1>")
        else:
            return PlainTextResponse(content="Welcome!")


@app.get("/welcome_token", status_code=200)
def come_token(token: str = "", format: Optional[str] = None):
    if token != app.s_token:
        raise HTTPException(status_code=401, detail="Wrong Passowrd or Username")
    else:
        if format == "json":
            return JSONResponse(content={"message": "Welcome!"})
        elif format == "html":
            return HTMLResponse(content="<h1>Welcome!</h1>")
        else:
            return PlainTextResponse(content="Welcome!")

@app.delete("/logout_session")
def session_out(session_token: str = Cookie(None), format: Optional[str] = None):
    if session_token != app.s_token or session_token == "":
        raise HTTPException(status_code=401, detail="Wrong Passowrd or Username")
    else:
        app.delete(app.s_token)
        return RedirectResponse(status_code=302, url=f"/logged_out?format={format}")

@app.delete("/logout_token")
def token_out(token: str = "", format: Optional[str] = None):
    if token != app.l_token or token == "":
        raise HTTPException(status_code=401, detail="Wrong Passowrd or Username")
    else:
        return RedirectResponse(status_code=302, url=f"/logged_out?format={format}")

@app.get("/logged_out", status_code=200)
def log_out(format: Optional[str] = None):
    if format == "json":
        return JSONResponse(content={"message": "Logged out!"})
    elif format == "html":
        return HTMLResponse(content="<h1>Logged out!</h1>")
    else:
        return PlainTextResponse(content="Logged out!")