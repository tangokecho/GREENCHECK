from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..models import (
    Base,
    SessionLocal,
    engine,
    Asset as AssetModel,
    MaintenanceRecord as MaintenanceRecordModel,
)

# Ensure tables are created
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class MaintenanceRecord(BaseModel):
    id: int
    description: str
    performed_on: date

    class Config:
        orm_mode = True


class MaintenanceRecordCreate(BaseModel):
    description: str
    performed_on: date | None = None


class Asset(BaseModel):
    id: int
    name: str
    description: str | None = None
    maintenance_records: List[MaintenanceRecord] = []

    class Config:
        orm_mode = True


class AssetCreate(BaseModel):
    name: str
    description: str | None = None


class AssetUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("/", response_model=Asset)
def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    db_asset = AssetModel(**asset.dict())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


@router.get("/", response_model=List[Asset])
def list_assets(db: Session = Depends(get_db)):
    return db.query(AssetModel).all()


@router.get("/{asset_id}", response_model=Asset)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.get(AssetModel, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.put("/{asset_id}", response_model=Asset)
def update_asset(asset_id: int, asset: AssetUpdate, db: Session = Depends(get_db)):
    db_asset = db.get(AssetModel, asset_id)
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    for key, value in asset.dict(exclude_unset=True).items():
        setattr(db_asset, key, value)
    db.commit()
    db.refresh(db_asset)
    return db_asset


@router.delete("/{asset_id}")
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.get(AssetModel, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    db.delete(asset)
    db.commit()
    return {"ok": True}


@router.post("/{asset_id}/maintenance", response_model=MaintenanceRecord)
def create_maintenance_record(
    asset_id: int, record: MaintenanceRecordCreate, db: Session = Depends(get_db)
):
    if not db.get(AssetModel, asset_id):
        raise HTTPException(status_code=404, detail="Asset not found")
    db_record = MaintenanceRecordModel(
        asset_id=asset_id,
        description=record.description,
        performed_on=record.performed_on or date.today(),
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.get("/{asset_id}/maintenance", response_model=List[MaintenanceRecord])
def list_maintenance(asset_id: int, db: Session = Depends(get_db)):
    return (
        db.query(MaintenanceRecordModel)
        .filter(MaintenanceRecordModel.asset_id == asset_id)
        .all()
    )


@router.delete("/{asset_id}/maintenance/{record_id}")
def delete_maintenance_record(
    asset_id: int, record_id: int, db: Session = Depends(get_db)
):
    record = db.get(MaintenanceRecordModel, record_id)
    if not record or record.asset_id != asset_id:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"ok": True}
