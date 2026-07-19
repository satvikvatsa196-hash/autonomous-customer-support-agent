from langchain_core.tools import tool
from pydantic import BaseModel, Field
from app.database.session import SessionLocal
from app.services import orders, tickets

# Dependency helper to get a fresh DB session for tools
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

from typing import Optional

# 1. Search Orders Tool
class SearchOrdersInput(BaseModel):
    user_id: Optional[int] = Field(None, description="The ID of the user to search orders for")

@tool("search_orders", args_schema=SearchOrdersInput)
def search_orders(user_id: int) -> str:
    """Search for all orders placed by a specific user."""
    db = get_db()
    user_orders = orders.get_orders_by_user(db, user_id)
    if not user_orders:
        return f"No orders found for user ID {user_id}."
    
    result = [f"Order ID: {o.id}, Product: {o.product_name}, Status: {o.status}" for o in user_orders]
    return "\n".join(result)

# 2. Check Shipping Status Tool
class CheckShippingStatusInput(BaseModel):
    order_id: Optional[int] = Field(None, description="The ID of the order to check shipping status")

@tool("check_shipping_status", args_schema=CheckShippingStatusInput)
def check_shipping_status(order_id: int) -> str:
    """Check the shipping status and tracking number of a specific order."""
    db = get_db()
    order = orders.get_order_by_id(db, order_id)
    if not order:
        return f"Order {order_id} not found."
    
    tracking = order.tracking_number if order.tracking_number else "No tracking number assigned yet."
    return f"Order {order_id} status is '{order.status}'. Tracking: {tracking}"

# 3. Refund Order Tool
class RefundOrderInput(BaseModel):
    order_id: Optional[int] = Field(None, description="The ID of the order to refund")

@tool("refund_order", args_schema=RefundOrderInput)
def refund_order(order_id: int) -> str:
    """Process a refund for a specific order."""
    db = get_db()
    order = orders.refund_order(db, order_id)
    if not order:
        return f"Order {order_id} not found or could not be refunded."
    return f"Successfully refunded Order {order_id}."

# 4. Create Ticket Tool
class CreateTicketInput(BaseModel):
    issue: Optional[str] = Field(None, description="Description of the issue or problem")

@tool("create_ticket", args_schema=CreateTicketInput)
def create_ticket(issue: str) -> str:
    """Create a new customer support ticket."""
    db = get_db()
    # Defaulting user_id to 1 for simplicity until Authentication is built
    ticket = tickets.create_ticket(db, user_id=1, issue=issue)
    return f"Ticket created successfully. Ticket ID: {ticket.id}, Status: {ticket.status}"

# Export the tools for the LangGraph agent to use
agent_tools = [search_orders, check_shipping_status, refund_order, create_ticket]
