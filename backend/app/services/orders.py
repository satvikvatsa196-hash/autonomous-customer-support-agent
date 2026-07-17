from sqlalchemy.orm import Session
from app.models.order import Order

def get_orders_by_user(db: Session, user_id: int):
    return db.query(Order).filter(Order.user_id == user_id).all()

def get_order_by_id(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()

def refund_order(db: Session, order_id: int):
    order = get_order_by_id(db, order_id)
    if not order:
        return None
    
    order.status = "refunded"
    db.commit()
    db.refresh(order)
    return order
