from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.models import Project, ConstructionInspection, InspectionPhoto
from app.schemas import schemas
from datetime import date

# Project CRUD operations
def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Project).offset(skip).limit(limit).all()

def get_project(db: Session, project_id: int):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, project_id: int, project: schemas.ProjectCreate):
    db_project = get_project(db, project_id)
    for key, value in project.model_dump().items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    db_project = get_project(db, project_id)
    db.delete(db_project)
    db.commit()
    return db_project

# Inspection CRUD operations
def get_inspections(db: Session, skip: int = 0, limit: int = 100, project_id: Optional[int] = None):
    query = db.query(ConstructionInspection)
    if project_id:
        query = query.filter(ConstructionInspection.project_id == project_id)
    return query.offset(skip).limit(limit).all()

def get_inspection(db: Session, inspection_id: int):
    inspection = db.query(ConstructionInspection).filter(ConstructionInspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
    return inspection

def create_inspection(db: Session, inspection: schemas.InspectionCreate):
    db_inspection = ConstructionInspection(**inspection.model_dump())
    db.add(db_inspection)
    db.commit()
    db.refresh(db_inspection)
    return db_inspection

def update_inspection(db: Session, inspection_id: int, inspection_update: schemas.InspectionUpdate):
    db_inspection = get_inspection(db, inspection_id)
    for key, value in inspection_update.model_dump().items():
        setattr(db_inspection, key, value)
    db.commit()
    db.refresh(db_inspection)
    return db_inspection

def delete_inspection(db: Session, inspection_id: int):
    db_inspection = get_inspection(db, inspection_id)
    db.delete(db_inspection)
    db.commit()
    return db_inspection

# Photo CRUD operations
def get_photos(db: Session, skip: int = 0, limit: int = 100, inspection_id: Optional[int] = None):
    query = db.query(InspectionPhoto)
    if inspection_id:
        query = query.filter(InspectionPhoto.inspection_id == inspection_id)
    return query.offset(skip).limit(limit).all()

def get_photo(db: Session, photo_id: int):
    photo = db.query(InspectionPhoto).filter(InspectionPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return photo

def create_photo(db: Session, photo: schemas.PhotoCreate):
    db_photo = InspectionPhoto(**photo.model_dump())
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo

def update_photo(db: Session, photo_id: int, photo_update: schemas.PhotoUpdate):
    db_photo = get_photo(db, photo_id)
    update_data = photo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_photo, key, value)
    db.commit()
    db.refresh(db_photo)
    return db_photo

def delete_photo(db: Session, photo_id: int):
    db_photo = get_photo(db, photo_id)
    db.delete(db_photo)
    db.commit()
    return db_photo
