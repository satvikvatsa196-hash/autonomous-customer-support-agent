from sqlalchemy.orm import Session
from app.models.ticket import Ticket

def create_ticket(db: Session, user_id: int, issue: str):
    new_ticket = Ticket(user_id=user_id, issue=issue, status="open")
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket
