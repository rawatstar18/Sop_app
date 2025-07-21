from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import user

app = FastAPI()

# Allow frontend from port 5500
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],   # Allow POST, OPTIONS, etc.
    allow_headers=["*"],
)

app.include_router(user.router)
