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
import sqlite3


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


@app.post("/login_session", status_code=201)
def login_session(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")

    if not (correct_password and correct_username):
        raise HTTPException(status_code=401, detail="Wrong Passowrd or Username")
    else:
        s_code = str(randint(0,1000))
        session_token = hashlib.sha256(f"{s_code}4dm1n:NotSoSecurePa$${s_code}".encode()).hexdigest()
        response.set_cookie(key="session_token", value=f"{session_token}")
        response.status_code = status.HTTP_201_CREATED
        if len(app.s_token) >= 3:
            app.s_token.pop(0)
        app.s_token.append(session_token)
        return {"session_token": f"{session_token}"}

@app.post("/login_token", status_code=201)
def login_token(*, response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")

    if not (correct_password and correct_username):
        raise HTTPException(status_code=401, detail="Wrong Passowrd or Username")
    else:
        s_code = randint(0, 1000)
        token = hashlib.sha256(f"{s_code}4dm1n:NotSoSecurePa$${s_code}".encode()).hexdigest()
        response.status_code = status.HTTP_201_CREATED
        if len(app.l_token) >= 3:
            app.l_token.pop(0)
        app.l_token.append(token)
        return {"token": f"{token}"}


@app.get("/welcome_session", status_code=200)
def come_session(session_token: str = Cookie(None), format: Optional[str] = None):
    if session_token not in app.s_token:
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
    if token not in app.s_token:
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
    if session_token not in app.s_token or session_token == "":
        raise HTTPException(status_code=401, detail="Wrong Passowrd or Username")
    else:
        app.s_token.remove(session_token)
        return RedirectResponse(status_code=302, url=f"/logged_out?format={format}")

@app.delete("/logout_token")
def token_out(token: str = "", format: Optional[str] = None):
    if token not in app.l_token or token == "":
        raise HTTPException(status_code=401, detail="Wrong Passowrd or Username")
    else:
        app.l_token.remove(token)
        return RedirectResponse(status_code=302, url=f"/logged_out?format={format}")

@app.get("/logged_out", status_code=200)
def log_out(format: Optional[str] = None):
    if format == "json":
        return JSONResponse(content={"message": "Logged out!"})
    elif format == "html":
        return HTMLResponse(content="<h1>Logged out!</h1>")
    else:
        return PlainTextResponse(content="Logged out!")


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.row_factory = sqlite3.Row
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/categories")
async def ret_categories():
    categories = app.db_connection.execute("SELECT CategoryID as id, CategoryName as name FROM  Categories").fetchall()
    return {
        "categories": categories
    }

@app.get("/customers")
async def ret_customers():
    categories = app.db_connection.execute("SELECT CustomerId AS id, CompanyName AS name,"
                                "Address || ' ' || PostalCode || ' ' || City || ' ' || Country AS full_address "
                                "FROM customers").fetchall()
    return {
        'customers': categories
    }


@app.get("/products/{product_id}")
async def get_prduct_id(product_id: int):
    id_name = app.db_connection.execute(
        "SELECT ProductId AS id, ProductName AS name FROM Products WHERE ProductId = :product_id", {"product_id": product_id}
        ).fetchone()

    if id_name:
        return {"id": id_name[0], "name": id_name[1]}
    else:
        raise HTTPException(status_code=404, detail="Wrong ID")

@app.get("/employees")
async def get_emps(limit: Optional[int] = -1, offset: Optional[int] = 0, order: Optional[str] = "id"):
    if order not in ["first_name", "last_name", "city", "id"]:
        raise HTTPException(status_code=400, detail="Wrong order")

    info = app.db_connection.execute(
        "SELECT EmployeeID AS id, LastName AS last_name, FirstName AS first_name, City AS city FROM Employees "
        f"ORDER BY {order} LIMIT :limit OFFSET :offset",
        {"limit": limit, "offset": offset}
        ).fetchall()
    return {
    "employees": info
    }

@app.get("/products_extended")
async def get_products():
    products_info = app.db_connection.execute(
    """
    SELECT Products.ProductID as id, Products.ProductName as name, 
    Categories.CategoryName as category, Suppliers.CompanyName as supplier
    FROM Products JOIN Categories ON Products.CategoryID = Categories.CategoryID 
    Join Suppliers ON Products.SupplierID = Suppliers.SupplierID ORDER BY Products.ProductID
    """
    ).fetchall()

    return {
        "products_extended": products_info
    }


@app.get("/products/{id}/orders")
async def get_products_by_id(product_id: int):
    products_info = app.db_connection.execute(
        f'''SELECT Products.ProductID, Orders.OrderID AS id, Customers.CompanyName AS customer, 
        [Order Details].Quantity AS quantity, [Order Details].UnitPrice AS unit_price,
        [Order Details].Discount as discount 
        FROM Products JOIN [Order Details] ON Products.ProductID = [Order Details].ProductID JOIN Orders 
        ON [Order Details].OrderID = Orders.OrderID JOIN Customers 
        ON Orders.CustomerID = Customers.CustomerID 
        WHERE Products.ProductID = {product_id} ORDER BY Orders.OrderID
    ''').fetchall()

    if products_info == []:
        raise HTTPException(status_code=404, detail="Wrong ID")
    else:
        total_price = (products_info["unit_price"] * products_info["quantity"]) - \
                      (products_info["discount"] * (products_info["unit_price"] * products_info["quantity"]))
        ret_prod_info = [{"id": i["id"], "customer": i["customer"], "quantity": i["quantity"],
                          "total_price": total_price} for i in products_info]
        return {
            "orders": ret_prod_info
        }

