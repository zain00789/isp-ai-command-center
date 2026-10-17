
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.ai_chat import router as ai_chat_router
from backend.customers import router as customers_router
from backend.ai import router as ai_router
from backend.voice import router as voice_router


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(ai_chat_router, prefix="/api/v1")
app.include_router(voice_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
