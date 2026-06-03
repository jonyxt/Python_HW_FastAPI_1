# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base

class Advertisement(Base):
    __tablename__ = 'advertisements'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    owner = Column(String, nullable=False)
    create_time = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'owner': self.owner,
            'create_time': self.create_time.isoformat() if self.create_time else None,
        }