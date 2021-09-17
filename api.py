from typing import Dict
import os
import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def root() -> Dict[str, str]:
    a = 'a'
    b = 'b' + a
    return {'hello world': b}


if __name__ == '__main__':
    PORT_STR = os.getenv('PORT')
    if PORT_STR is None:
        raise Exception('PORT not defined')
    PORT = int(PORT_STR)
    uvicorn.run(app, host='0.0.0.0', port=PORT)
