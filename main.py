from fastapi import FastAPI, Response, status

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.get("/method", status_code=200)
def get_method(response: Response):
    response.status_code = status.HTTP_200_OK
    return {"method": "GET"}

@app.options("/method", status_code=200)
def get_method(response: Response):
    response.status_code = status.HTTP_200_OK
    return {"method": "OPTIONS"}

@app.put("/method", status_code=200)
def get_method(response: Response):
    response.status_code = status.HTTP_200_OK
    return {"method": "PUT"}

@app.delete("/method", status_code=200)
def get_method(response: Response):
    response.status_code = status.HTTP_200_OK
    return {"method": "DELETE"}

@app.post("/method", status_code=201)
def get_method(response: Response):
    response.status_code = status.HTTP_201_CREATED
    return {"method": "POST"}

