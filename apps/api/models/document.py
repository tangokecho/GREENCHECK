from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from . import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    maintenance_record_id = Column(Integer, ForeignKey("maintenance_records.id"), nullable=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=True)

    asset = relationship("Asset", back_populates="documents")
    maintenance_record = relationship(
        "MaintenanceRecord", back_populates="documents"
    )
