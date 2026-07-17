from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage

from app.database.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.ai_agent.graph import app as agent_app

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Basic endpoint to interact with the LangGraph agent.
    Currently, it processes the single incoming message without database history retrieval.
    """
    try:
        # Construct the input state
        inputs = {"messages": [HumanMessage(content=request.message)]}
        
        # Invoke the LangGraph workflow
        output = agent_app.invoke(inputs)
        
        # The output state contains all messages. The last one is the AI's response.
        ai_message = output["messages"][-1]
        
        return ChatResponse(reply=ai_message.content)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
