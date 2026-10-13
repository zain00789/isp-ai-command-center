
from fastapi import FastAPI
from backend.customers import router as customers_router

app = FastAPI()

app.include_router(customers_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}
