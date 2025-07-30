# SQLAlchemy model definitions
from sqlalchemy import Column, Integer, String
from .base import Base

# Example model - replace with your actual database models
class Example(Base):
    __tablename__ = 'examples'
    
    id = Column(Integer, primary_key=True)
    field1 = Column(String)
    field2 = Column(Integer)
