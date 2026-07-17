from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, messages_from_dict, messages_to_dict

from app.database.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.ai_agent.graph import app as agent_app
from app.models.conversation import Conversation
from app.models.user import User

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint to interact with the LangGraph agent, featuring PostgreSQL memory.
    It retrieves previous conversation context before invoking the agent.
    """
    try:
        # 1. Fetch or create the conversation from PostgreSQL
        conversation = db.query(Conversation).filter(Conversation.id == request.session_id).first()
        
        if not conversation:
            # Auto-create a demo user if it doesn't exist (for internship project ease of use)
            user = db.query(User).filter(User.id == 1).first()
            if not user:
                user = User(id=1, name="Demo User", email="demo@example.com")
                db.add(user)
                db.commit()
                
            # Create a fresh conversation
            conversation = Conversation(id=request.session_id, user_id=1, messages=[])
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        # 2. Deserialize previous messages from JSON
        history_dicts = conversation.messages if conversation.messages else []
        history = messages_from_dict(history_dicts)
        
        # 3. Append the new user message
        new_message = HumanMessage(content=request.message)
        inputs = {"messages": history + [new_message]}
        
        # 4. Invoke LangGraph with the full historical context
        output = agent_app.invoke(inputs)
        
        # 5. Extract the updated message history and serialize back to dicts
        updated_messages = output["messages"]
        conversation.messages = messages_to_dict(updated_messages)
        
        # Save to PostgreSQL
        db.commit()
        
        # 6. Return the final AI response to the frontend
        ai_message = updated_messages[-1]
        return ChatResponse(reply=ai_message.content)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
