from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.params import Body
# from pydantic import BaseModel
# from . import schemas, utils
# from typing import Optional, List
# from random import randrange
# import mysql.connector
# from mysql.connector import errorcode
# import time
from .routers import post, user, auth, vote

"""
The command below starts the server. It will be the machin elocalhost
for example; http://127.0.0.1:8000

uvicorn app.main:app --reload

The --reload modifier should be use in development only
"""
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

"""
Bellow, the decorator, the method and the path
The position in the file of the path is important
The code will be scanned top down and the first path operation that matches the request will trigger.
"""


# Hello World
@app.get("/")
def root():
    return {"message": "Hello World!"}
