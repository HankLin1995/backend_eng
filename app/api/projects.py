from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.services import crud
from app.schemas import schemas

router = APIRouter()

@router.post("/projects/", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project"""
    return crud.create_project(db=db, project=project)

@router.get("/projects/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all projects"""
    projects = crud.get_projects(db, skip=skip, limit=limit)
    return projects

@router.get("/projects/{project_id}", response_model=schemas.ProjectWithInspections)
def read_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project by ID with its inspections"""
    project = crud.get_project(db, project_id=project_id)
    return project

@router.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    """Update a project"""
    return crud.update_project(db=db, project_id=project_id, project=project)

@router.delete("/projects/{project_id}", response_model=schemas.Project)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project"""
    return crud.delete_project(db=db, project_id=project_id)
