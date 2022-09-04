import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from src.api import router

import sys
sys.dont_write_bytecode = True

app = FastAPI()

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=5001)
    print("running")