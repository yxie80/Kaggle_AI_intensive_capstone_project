"""FastAPI backend for the restaurant recommender system"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncio
from runner.orchestrator_runner import OrchestratorRunner

app = FastAPI(
    title="Restaurant Recommender API",
    description="Multi-agent restaurant recommendation system",
    version="1.0.0"
)

# Initialize orchestrator runner
orchestrator = OrchestratorRunner()


class ChatRequest(BaseModel):
    """Chat request model"""
    user_id: str
    message: str
    context_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    context_id: str
    message: str
    next_step: str
    status: str = "ok"


class StateResponse(BaseModel):
    """Conversation state response"""
    context_id: str
    user_id: str
    status: str
    data: dict


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - process user message
    
    If context_id is None, starts a new conversation.
    Otherwise, continues existing conversation.
    """
    try:
        if not request.context_id:
            # Start new conversation
            result = await orchestrator.start_conversation(
                request.user_id,
                request.message
            )
        else:
            # Continue conversation
            result = await orchestrator.process_message(
                request.context_id,
                request.message
            )
        
        return ChatResponse(
            context_id=result.get("context_id", ""),
            message=result.get("message", ""),
            next_step=result.get("next_step", "unknown")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/state/{context_id}", response_model=StateResponse)
async def get_state(context_id: str):
    """Get current conversation state"""
    state = orchestrator.state_store.get_state(context_id)
    
    if not state:
        raise HTTPException(status_code=404, detail="Context not found")
    
    return StateResponse(
        context_id=context_id,
        user_id=state.user_id,
        status="active",
        data=state.to_dict()
    )


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "restaurant-recommender"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Restaurant Recommender API",
        "endpoints": {
            "chat": "POST /chat",
            "state": "GET /state/{context_id}",
            "health": "GET /health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
