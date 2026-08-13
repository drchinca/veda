from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="VEDA Sample API")
app.include_router(router)
