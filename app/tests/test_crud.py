import pytest
from fastapi import HTTPException
from datetime import date, timedelta
from app.services.crud import (
    get_projects, get_project, create_project, update_project, delete_project,
    get_inspections, get_inspection, create_inspection, update_inspection, delete_inspection,
    get_photos, get_photo, create_photo, update_photo, delete_photo
)
from app.schemas import schemas
from app.models.models import Project, ConstructionInspection, InspectionPhoto

# Project CRUD tests
def test_create_project(db):
    """Test creating a project"""
    project_data = schemas.ProjectCreate(
        name="Test Project",
        location="Test Location",
        contractor="Test Contractor",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    
    project = create_project(db, project_data)
    assert project.id is not None
    assert project.name == "Test Project"
    assert project.location == "Test Location"
    assert project.contractor == "Test Contractor"
    assert project.start_date == date.today()
    assert project.end_date == date.today() + timedelta(days=30)

def test_get_project(db):
    """Test getting a project by ID"""
    # Create a project first
    project_data = schemas.ProjectCreate(
        name="Test Project",
        location="Test Location",
        contractor="Test Contractor",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    created_project = create_project(db, project_data)
    
    # Get the project
    project = get_project(db, created_project.id)
    assert project.id == created_project.id
    assert project.name == "Test Project"

def test_get_project_not_found(db):
    """Test getting a non-existent project"""
    with pytest.raises(HTTPException) as excinfo:
        get_project(db, 999)
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Project not found"

def test_get_projects(db):
    """Test getting all projects"""
    # Create some projects
    project_data1 = schemas.ProjectCreate(
        name="Test Project 1",
        location="Test Location 1",
        contractor="Test Contractor 1",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    project_data2 = schemas.ProjectCreate(
        name="Test Project 2",
        location="Test Location 2",
        contractor="Test Contractor 2",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=60)
    )
    
    create_project(db, project_data1)
    create_project(db, project_data2)
    
    # Get all projects
    projects = get_projects(db)
    assert len(projects) == 2
    project_names = [p.name for p in projects]
    assert "Test Project 1" in project_names
    assert "Test Project 2" in project_names

def test_update_project(db):
    """Test updating a project"""
    # Create a project first
    project_data = schemas.ProjectCreate(
        name="Test Project",
        location="Test Location",
        contractor="Test Contractor",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    created_project = create_project(db, project_data)
    
    # Update the project
    updated_data = schemas.ProjectCreate(
        name="Updated Project",
        location="Updated Location",
        contractor="Updated Contractor",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=45)
    )
    
    updated_project = update_project(db, created_project.id, updated_data)
    assert updated_project.id == created_project.id
    assert updated_project.name == "Updated Project"
    assert updated_project.location == "Updated Location"
    assert updated_project.contractor == "Updated Contractor"
    assert updated_project.end_date == date.today() + timedelta(days=45)

def test_delete_project(db):
    """Test deleting a project"""
    # Create a project first
    project_data = schemas.ProjectCreate(
        name="Test Project",
        location="Test Location",
        contractor="Test Contractor",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    created_project = create_project(db, project_data)
    
    # Delete the project
    deleted_project = delete_project(db, created_project.id)
    assert deleted_project.id == created_project.id
    
    # Verify it's deleted
    with pytest.raises(HTTPException) as excinfo:
        get_project(db, created_project.id)
    assert excinfo.value.status_code == 404

# Inspection CRUD tests
def test_create_inspection(db):
    """Test creating an inspection"""
    # Create a project first
    project_data = schemas.ProjectCreate(
        name="Test Project",
        location="Test Location",
        contractor="Test Contractor",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    project = create_project(db, project_data)
    
    # Create inspection
    inspection_data = schemas.InspectionCreate(
        project_id=project.id,
        subproject_name="Test Subproject",
        inspection_form_name="Test Form",
        inspection_date=date.today(),
        location="Test Location",
        timing="檢驗停留點",
        result="合格",
        remark="Test remark"
    )
    
    inspection = create_inspection(db, inspection_data)
    assert inspection.id is not None
    assert inspection.project_id == project.id
    assert inspection.subproject_name == "Test Subproject"
    assert inspection.timing == "檢驗停留點"
    assert inspection.result == "合格"

def test_get_inspection(db):
    """Test getting an inspection by ID"""
    # Create a project first
    project_data = schemas.ProjectCreate(
        name="Test Project",
        location="Test Location",
        contractor="Test Contractor",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    project = create_project(db, project_data)
    
    # Create inspection
    inspection_data = schemas.InspectionCreate(
        project_id=project.id,
        subproject_name="Test Subproject",
        inspection_form_name="Test Form",
        inspection_date=date.today(),
        location="Test Location",
        timing="檢驗停留點",
        result="合格",
        remark="Test remark"
    )
    created_inspection = create_inspection(db, inspection_data)
    
    # Get the inspection
    inspection = get_inspection(db, created_inspection.id)
    assert inspection.id == created_inspection.id
    assert inspection.subproject_name == "Test Subproject"

def test_update_inspection(db):
    """Test updating an inspection"""
    # Create a project first
    project_data = schemas.ProjectCreate(
        name="Test Project",
        location="Test Location",
        contractor="Test Contractor",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    project = create_project(db, project_data)
    
    # Create inspection
    inspection_data = schemas.InspectionCreate(
        project_id=project.id,
        subproject_name="Test Subproject",
        inspection_form_name="Test Form",
        inspection_date=date.today(),
        location="Test Location",
        timing="檢驗停留點",
        result="合格",
        remark="Test remark"
    )
    created_inspection = create_inspection(db, inspection_data)
    
    # Update the inspection
    update_data = schemas.InspectionUpdate(
        result="不合格",
        remark="Updated remark",
        pdf_path="/path/to/pdf"
    )
    
    updated_inspection = update_inspection(db, created_inspection.id, update_data)
    assert updated_inspection.id == created_inspection.id
    assert updated_inspection.result == "不合格"
    assert updated_inspection.remark == "Updated remark"
    assert updated_inspection.pdf_path == "/path/to/pdf"

# Photo CRUD tests
def test_create_photo(db):
    """Test creating a photo"""
    # Create a project first
    project_data = schemas.ProjectCreate(
        name="Test Project",
        location="Test Location",
        contractor="Test Contractor",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    project = create_project(db, project_data)
    
    # Create inspection
    inspection_data = schemas.InspectionCreate(
        project_id=project.id,
        subproject_name="Test Subproject",
        inspection_form_name="Test Form",
        inspection_date=date.today(),
        location="Test Location",
        timing="檢驗停留點",
        result="合格",
        remark="Test remark"
    )
    inspection = create_inspection(db, inspection_data)
    
    # Create photo
    photo_data = schemas.PhotoCreate(
        inspection_id=inspection.id,
        photo_path="/path/to/photo.jpg",
        capture_date=date.today(),
        caption="Test Caption"
    )
    
    photo = create_photo(db, photo_data)
    assert photo.id is not None
    assert photo.inspection_id == inspection.id
    assert photo.photo_path == "/path/to/photo.jpg"
    assert photo.caption == "Test Caption"

def test_get_photos_by_inspection(db):
    """Test getting photos by inspection ID"""
    # Create a project first
    project_data = schemas.ProjectCreate(
        name="Test Project",
        location="Test Location",
        contractor="Test Contractor",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    project = create_project(db, project_data)
    
    # Create inspection
    inspection_data = schemas.InspectionCreate(
        project_id=project.id,
        subproject_name="Test Subproject",
        inspection_form_name="Test Form",
        inspection_date=date.today(),
        location="Test Location",
        timing="檢驗停留點",
        result="合格",
        remark="Test remark"
    )
    inspection = create_inspection(db, inspection_data)
    
    # Create photos
    photo_data1 = schemas.PhotoCreate(
        inspection_id=inspection.id,
        photo_path="/path/to/photo1.jpg",
        capture_date=date.today(),
        caption="Test Caption 1"
    )
    
    photo_data2 = schemas.PhotoCreate(
        inspection_id=inspection.id,
        photo_path="/path/to/photo2.jpg",
        capture_date=date.today(),
        caption="Test Caption 2"
    )
    
    create_photo(db, photo_data1)
    create_photo(db, photo_data2)
    
    # Get photos by inspection ID
    photos = get_photos(db, inspection_id=inspection.id)
    assert len(photos) == 2
    photo_paths = [p.photo_path for p in photos]
    assert "/path/to/photo1.jpg" in photo_paths
    assert "/path/to/photo2.jpg" in photo_paths
