from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import endpoints

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # フロントと通信できるように
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router)
