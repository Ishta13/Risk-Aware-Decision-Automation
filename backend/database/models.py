from sqlalchemy import Column, Integer, Float, String, JSON, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class DecisionLog(Base):
    __tablename__ = "decision_logs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    decision = Column(String)
    final_confidence = Column(Float)
    model_confidence = Column(Float)
    data_quality_score = Column(Float)
    missing_ratio = Column(Float)
    payload = Column(JSON)
    explanation = Column(JSON)
