import os
import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    a = "a"
    b = "b" + a
    return {"hello world": b}


if __name__ == "__main__":
    PORT = int(os.getenv('PORT'))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
