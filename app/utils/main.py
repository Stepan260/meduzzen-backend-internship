from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }
