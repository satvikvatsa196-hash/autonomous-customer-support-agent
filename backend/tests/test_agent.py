from langchain_core.messages import HumanMessage, AIMessage
from app.ai_agent.graph import should_continue

def test_agent_routing_shipping_tool():
    """
    Test: Input: 'Where is my order?'
    Expected: shipping tool is called
    We simulate the LLM's output by injecting a mock AIMessage with a tool_call.
    """
    state = {
        "messages": [
            HumanMessage(content="Where is my order?"),
            AIMessage(
                content="Intent: shipping_status\nAction: check_shipping_status",
                tool_calls=[{"name": "check_shipping_status", "args": {"order_id": "123"}, "id": "call_abc"}]
            )
        ]
    }
    
    # The should_continue edge function decides the route
    route = should_continue(state)
    assert route == "tools", "Agent did not route to tools when shipping tool was requested."

def test_agent_routing_rag_retrieval():
    """
    Test: Input: 'What is your refund policy?'
    Expected: RAG retrieval is used
    We simulate the LLM outputting the knowledge_base intent text.
    """
    state = {
        "messages": [
            HumanMessage(content="What is your refund policy?"),
            AIMessage(
                content="Intent: knowledge_base\nAction: trigger_rag"
            )
        ]
    }
    
    # The should_continue edge function intercepts this text and routes to RAG
    route = should_continue(state)
    assert route == "rag", "Agent did not route to RAG for policy question."
