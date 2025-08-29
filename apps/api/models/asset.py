from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from . import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    maintenance_records = relationship(
        "MaintenanceRecord", back_populates="asset", cascade="all, delete-orphan"
    )
    documents = relationship(
        "Document", back_populates="asset", cascade="all, delete-orphan"
    )
