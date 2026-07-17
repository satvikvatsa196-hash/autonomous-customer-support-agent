from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from app.ai_agent.state import AgentState
from app.ai_agent.prompts import SYSTEM_PROMPT
from app.ai_agent.tools import agent_tools
from app.utils.config import settings

# Initialize the LLM and bind the tools
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=settings.OPENAI_API_KEY)
llm_with_tools = llm.bind_tools(agent_tools)

def call_model(state: AgentState):
    """
    Invokes the LLM with the messages. The LLM can decide to return a regular message
    or a tool invocation request.
    """
    messages = state['messages']
    
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    """
    Determines whether the agent needs to call a tool or if it has finished.
    """
    messages = state['messages']
    last_message = messages[-1]
    
    # If the LLM returned tool calls, we route to the "tools" node
    if last_message.tool_calls:
        return "tools"
    
    # Otherwise, it's a final response
    return END

# Define the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", call_model)
# ToolNode is a prebuilt LangGraph node that executes the functions requested by the LLM
workflow.add_node("tools", ToolNode(agent_tools))

# Define the edges
workflow.set_entry_point("agent")

# We use a conditional edge to decide if we should run tools or end
workflow.add_conditional_edges("agent", should_continue)

# After tools run, we always go back to the agent to interpret the tool output
workflow.add_edge("tools", "agent")

# Compile the graph
app = workflow.compile()
