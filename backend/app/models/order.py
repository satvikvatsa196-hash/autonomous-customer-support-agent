from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Order(Base):
    """
    Order model tracks the purchases of a User.
    Uses 'ondelete="CASCADE"' on the ForeignKey to let the database handle referential integrity.
    Status is a String for simplicity (could be an Enum in a more strict environment).
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="pending") 
    tracking_number = Column(String(100), nullable=True)

    # Relationships
    user = relationship("User", back_populates="orders")
