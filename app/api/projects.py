from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.services import crud
from app.schemas import schemas
from app.utils.file_utils import calculate_project_files_size

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

@router.get("/projects/{project_id}/storage")
def get_project_storage_info(project_id: int, db: Session = Depends(get_db)):
    """
    獲取特定專案的靜態檔案大小資訊
    
    Args:
        project_id: 專案ID
        db: 資料庫會話
        
    Returns:
        包含專案靜態檔案大小資訊的字典
    """
    # 檢查專案是否存在
    project = crud.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    # 計算專案相關的靜態檔案大小
    storage_info = calculate_project_files_size(db, project_id)
    return storage_info

@router.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    """Update a project"""
    return crud.update_project(db=db, project_id=project_id, project=project)

@router.delete("/projects/{project_id}", response_model=schemas.Project)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project"""
    return crud.delete_project(db=db, project_id=project_id)
