
from fastapi import APIRouter
from pydantic import BaseModel, Field

from agents.ai_service import process_customer_message


router = APIRouter(prefix="/ai", tags=["AI Agent"])


class AIRequest(BaseModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1)


class AIResponse(BaseModel):
    intent: str
    response: str
    action: str


@router.post("/respond", response_model=AIResponse)
def respond_to_customer(request: AIRequest):
    result = process_customer_message(
        message=request.message,
        session_id=request.session_id,
    )

    return AIResponse(**result)
