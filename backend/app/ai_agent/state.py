from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    The State represents the data that flows through the LangGraph agent.
    'messages' holds the conversation history. We use 'add_messages' 
    to append new messages to the existing list instead of overwriting it.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    
    # State tracking for missing parameters
    dialog_state: str  # e.g., "chat", "collecting_info", "escalating", "escalated"
    active_tool: str
    missing_params: list[str]
    
    # Escalation tracking
    escalation_reason: str
    tool_failure_count: int
