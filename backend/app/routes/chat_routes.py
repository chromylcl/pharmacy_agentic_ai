from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.langchain_agent import run_agent

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat(req: ChatRequest):

    response = run_agent(req.message)

    return {"response": response}