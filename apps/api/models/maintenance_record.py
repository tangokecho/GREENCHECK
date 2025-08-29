from datetime import date
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from . import Base


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    description = Column(String, nullable=False)
    performed_on = Column(Date, default=date.today)

    asset = relationship("Asset", back_populates="maintenance_records")
    documents = relationship(
        "Document", back_populates="maintenance_record", cascade="all, delete-orphan"
    )
