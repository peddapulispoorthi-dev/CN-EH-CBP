from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base

def get_utc_now():
    return datetime.now(timezone.utc)

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    target = Column(String, nullable=False)
    profile = Column(String, nullable=False)
    status = Column(String, default="Queued")
    created_at = Column(DateTime, default=get_utc_now)

    hosts = relationship("Host", back_populates="scan", cascade="all, delete-orphan", lazy="selectin")

class Host(Base):
    __tablename__ = "hosts"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), index=True)
    ip_address = Column(String, nullable=False)
    hostname = Column(String, nullable=True)
    status = Column(String, nullable=False)
    ports_data = Column(Text, nullable=True)

    scan = relationship("Scan", back_populates="hosts")
