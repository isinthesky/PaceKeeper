from sqlalchemy import Column, Integer, String, Text, SmallInteger, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False)
    description = Column(Text, nullable=False, default="")
    color = Column(String(7), nullable=False, default="#FFFFFF")
    state = Column(SmallInteger, default=1)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "state": self.state
        }
    
    def __repr__(self):
        return f"<id={self.id}, name='{self.name}', description='{self.description}'>"

class Tag(Base):
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False)
    description = Column(Text, nullable=True, default="")
    category_id = Column(Integer, nullable=False, default=0)
    state = Column(SmallInteger, default=1)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category_id": self.category_id,
            "state": self.state
        }
        
    def __repr__(self):
        return f"<id={self.id}, name='{self.name}', description='{self.description}', category_id='{self.category_id}'>"


class Log(Base):
    __tablename__ = 'pace_logs'
    
    id = Column(Integer, primary_key=True)
    message = Column(Text, nullable=False, default="")
    tags = Column(Text, nullable=False, default="")
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=True)
    state = Column(SmallInteger, default=1)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "message": self.message,
            "tags": self.tags,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "state": self.state
        }
    
    def __repr__(self):
        return f"<Log(message='{self.message}', tags='{self.tags}', start_date='{self.start_date}', end_date='{self.end_date}')>"