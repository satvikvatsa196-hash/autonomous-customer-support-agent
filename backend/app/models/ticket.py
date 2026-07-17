from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Ticket(Base):
    """
    Ticket model represents a support issue raised by a User.
    'issue' is Text to accommodate long descriptions.
    """
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    issue = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="open") 

    # Relationships
    user = relationship("User", back_populates="tickets")
