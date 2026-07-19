from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver

from app.ai_agent.state import AgentState
from app.ai_agent.prompts import SYSTEM_PROMPT
from app.ai_agent.tools import agent_tools
from app.ai_agent.rag import query_knowledge_base
from app.utils.config import settings

# Initialize the checkpointer
memory = MemorySaver()

# Initialize the LLM and bind the tools
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=settings.OPENAI_API_KEY)
llm_with_tools = llm.bind_tools(agent_tools)

def call_model(state: AgentState):
    """
    Invokes the LLM with the messages. The LLM can decide to return a regular message
    or a tool invocation request.
    """
    messages = state.get('messages', [])
    
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def validate_tool_params(state: AgentState):
    """
    Intercepts tool calls when required parameters are missing.
    Returns a ToolMessage with an error to force the LLM to ask the user.
    """
    messages = state.get('messages', [])
    last_message = messages[-1]
    
    missing_params = []
    active_tool = ""
    tool_messages = []
    
    if getattr(last_message, 'tool_calls', None):
        for tool_call in last_message.tool_calls:
            # Check if args are empty or if any parameter is None
            if not tool_call["args"]:
                # The LLM completely omitted the parameter
                missing_params.append("required_parameter")
                active_tool = tool_call["name"]
            else:
                for param_name, param_value in tool_call["args"].items():
                    if param_value is None or param_value == "":
                        missing_params.append(param_name)
                        active_tool = tool_call["name"]
            
            if missing_params:
                tool_msg = ToolMessage(
                    tool_call_id=tool_call["id"],
                    name=tool_call["name"],
                    content=f"Error: Missing required parameter '{', '.join(missing_params)}'. Please ask the user to provide this information before proceeding."
                )
                tool_messages.append(tool_msg)
    
    return {
        "messages": tool_messages,
        "dialog_state": "collecting_info",
        "active_tool": active_tool,
        "missing_params": missing_params
    }


def rag_node(state: AgentState):
    """
    Dedicated node for Retrieval-Augmented Generation.
    Searches ChromaDB based on the user's question.
    """
    messages = state['messages']
    # Find the latest human message to use as the search query
    user_query = ""
    for msg in reversed(messages):
        if msg.type == "human":
            user_query = msg.content
            break
            
    context = query_knowledge_base(user_query)
    
    # Pass the context back to the agent as a system prompt instruction
    rag_message = SystemMessage(content=f"RAG Context Retrieved for user query:\n{context}\n\nPlease use this context to answer the user's question.")
    return {"messages": [rag_message]}

def should_continue(state: AgentState):
    """
    Determines whether the agent needs to call a tool, use RAG, or if it has finished.
    """
    messages = state.get('messages', [])
    last_message = messages[-1]
    
    # 1. Route to tools if the LLM called a tool
    if getattr(last_message, 'tool_calls', None):
        # Check if parameters are missing or args are completely empty
        for tc in last_message.tool_calls:
            if not tc["args"] or any(v is None or v == "" for v in tc["args"].values()):
                return "validate_tool_params"
        return "tools"
    
    # 2. Route to RAG node if the LLM identified a policy question
    if last_message.content and "Intent: knowledge_base" in last_message.content:
        # Prevent infinite loops if RAG was just executed in the previous step
        if len(messages) >= 2 and messages[-2].type == "system" and "RAG Context Retrieved" in messages[-2].content:
            return END
        return "rag"
    
    # 3. Otherwise, it's a final response
    return END

# Define the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(agent_tools))
workflow.add_node("validate_tool_params", validate_tool_params)
workflow.add_node("rag", rag_node)  # RAG explicitly added as a LangGraph node

# Define the edges
workflow.set_entry_point("agent")

# Conditional edge based on intent
workflow.add_conditional_edges("agent", should_continue)

# Both tools and RAG loop back to the agent to interpret the result
workflow.add_edge("tools", "agent")
workflow.add_edge("validate_tool_params", "agent")
workflow.add_edge("rag", "agent")

# Compile the graph with the checkpointer
app = workflow.compile(checkpointer=memory)
