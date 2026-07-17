from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from app.ai_agent.state import AgentState
from app.ai_agent.prompts import SYSTEM_PROMPT
from app.utils.config import settings

# Initialize the LLM
# This expects the OPENAI_API_KEY environment variable to be set.
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=settings.OPENAI_API_KEY)

def call_model(state: AgentState):
    """
    This is the core node of our graph. It receives the current state,
    invokes the LLM with the messages, and returns the LLM's response.
    """
    messages = state['messages']
    
    # Prepend the system prompt if it's not already there
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        
    response = llm.invoke(messages)
    
    # Return the new message to be appended to the state
    return {"messages": [response]}

# Define the graph
workflow = StateGraph(AgentState)

# Add our single node
workflow.add_node("agent", call_model)

# Define the edges (Flow: Start -> Agent -> End)
workflow.set_entry_point("agent")
workflow.add_edge("agent", END)

# Compile the graph into an executable application
app = workflow.compile()
