
from fastapi import FastAPI
from backend.ai_chat import router as ai_chat_router
from backend.customers import router as customers_router
from backend.ai import router as ai_router


app = FastAPI()

app.include_router(customers_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(ai_chat_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}
