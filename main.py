from fastapi import FastAPI, Response, status

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello world!"}

@app.get("/method")
def get_method():
    return {"method": "GET"}


