import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
import json
from app.main import app

client = TestClient(app)

def test_read_main(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Construction Inspection API"}

# Project API tests
def test_create_project(client):
    """Test creating a project via API"""
    project_data = {
        "name": "Test Project",
        "location": "Test Location",
        "contractor": "Test Contractor",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30))
    }
    
    response = client.post("/api/projects/", json=project_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["location"] == "Test Location"
    assert data["contractor"] == "Test Contractor"
    assert "id" in data

def test_read_projects(client):
    """Test reading all projects via API"""
    # Create a project first
    project_data = {
        "name": "Test Project",
        "location": "Test Location",
        "contractor": "Test Contractor",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30))
    }
    client.post("/api/projects/", json=project_data)
    
    # Get all projects
    response = client.get("/api/projects/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(project["name"] == "Test Project" for project in data)

def test_read_project(client):
    """Test reading a specific project via API"""
    # Create a project first
    project_data = {
        "name": "Test Project",
        "location": "Test Location",
        "contractor": "Test Contractor",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30))
    }
    create_response = client.post("/api/projects/", json=project_data)
    project_id = create_response.json()["id"]
    
    # Get the project
    response = client.get(f"/api/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Test Project"
    assert "inspections" in data

# Inspection API tests
def test_create_inspection(client):
    """Test creating an inspection via API"""
    # Create a project first
    project_data = {
        "name": "Test Project",
        "location": "Test Location",
        "contractor": "Test Contractor",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30))
    }
    create_response = client.post("/api/projects/", json=project_data)
    project_id = create_response.json()["id"]
    
    # Create an inspection
    inspection_data = {
        "project_id": project_id,
        "subproject_name": "Test Subproject",
        "inspection_form_name": "Test Form",
        "inspection_date": str(date.today()),
        "location": "Test Location",
        "timing": "檢驗停留點",
        "result": "合格",
        "remark": "Test remark"
    }
    
    response = client.post("/api/inspections/", json=inspection_data)
    assert response.status_code == 201
    data = response.json()
    assert data["project_id"] == project_id
    assert data["subproject_name"] == "Test Subproject"
    assert data["timing"] == "檢驗停留點"
    assert data["result"] == "合格"
    assert "id" in data

def test_read_inspections(client):
    """Test reading all inspections via API"""
    # Create a project first
    project_data = {
        "name": "Test Project",
        "location": "Test Location",
        "contractor": "Test Contractor",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30))
    }
    create_response = client.post("/api/projects/", json=project_data)
    project_id = create_response.json()["id"]
    
    # Create an inspection
    inspection_data = {
        "project_id": project_id,
        "subproject_name": "Test Subproject",
        "inspection_form_name": "Test Form",
        "inspection_date": str(date.today()),
        "location": "Test Location",
        "timing": "檢驗停留點",
        "result": "合格",
        "remark": "Test remark"
    }
    client.post("/api/inspections/", json=inspection_data)
    
    # Get all inspections
    response = client.get("/api/inspections/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(inspection["subproject_name"] == "Test Subproject" for inspection in data)
    
    # Get inspections filtered by project_id
    response = client.get(f"/api/inspections/?project_id={project_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(inspection["project_id"] == project_id for inspection in data)

def test_update_inspection(client):
    """Test updating an inspection via API"""
    # Create a project first
    project_data = {
        "name": "Test Project",
        "location": "Test Location",
        "contractor": "Test Contractor",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30))
    }
    create_response = client.post("/api/projects/", json=project_data)
    project_id = create_response.json()["id"]
    
    # Create an inspection
    inspection_data = {
        "project_id": project_id,
        "subproject_name": "Test Subproject",
        "inspection_form_name": "Test Form",
        "inspection_date": str(date.today()),
        "location": "Test Location",
        "timing": "檢驗停留點",
        "result": "合格",
        "remark": "Test remark"
    }
    create_response = client.post("/api/inspections/", json=inspection_data)
    inspection_id = create_response.json()["id"]
    
    # Update the inspection
    update_data = {
        "result": "不合格",
        "remark": "Updated remark",
        "pdf_path": "/path/to/pdf"
    }
    
    response = client.put(f"/api/inspections/{inspection_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == inspection_id
    assert data["result"] == "不合格"
    assert data["remark"] == "Updated remark"
    assert data["pdf_path"] == "/path/to/pdf"

# Photo API tests
def test_read_photos(client):
    """Test reading all photos via API"""
    # Create a project first
    project_data = {
        "name": "Test Project",
        "location": "Test Location",
        "contractor": "Test Contractor",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30))
    }
    create_response = client.post("/api/projects/", json=project_data)
    project_id = create_response.json()["id"]
    
    # Create an inspection
    inspection_data = {
        "project_id": project_id,
        "subproject_name": "Test Subproject",
        "inspection_form_name": "Test Form",
        "inspection_date": str(date.today()),
        "location": "Test Location",
        "timing": "檢驗停留點",
        "result": "合格",
        "remark": "Test remark"
    }
    inspection_response = client.post("/api/inspections/", json=inspection_data)
    inspection_id = inspection_response.json()["id"]
    
    # Mock photo data (since we can't easily test file uploads in this context)
    # In a real test, you would use TestClient's files parameter to upload actual files
    
    # Get all photos
    response = client.get("/api/photos/")
    assert response.status_code == 200
    
    # Get photos filtered by inspection_id
    response = client.get(f"/api/photos/?inspection_id={inspection_id}")
    assert response.status_code == 200

def test_read_photo(client):
    """Test reading a specific photo via API"""
    # Create a project first
    project_data = {
        "name": "Test Project",
        "location": "Test Location",
        "contractor": "Test Contractor",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30))
    }
    create_response = client.post("/api/projects/", json=project_data)
    project_id = create_response.json()["id"]
    
    # Create an inspection
    inspection_data = {
        "project_id": project_id,
        "subproject_name": "Test Subproject",
        "inspection_form_name": "Test Form",
        "inspection_date": str(date.today()),
        "location": "Test Location",
        "timing": "檢驗停留點",
        "result": "合格",
        "remark": "Test remark"
    }
    inspection_response = client.post("/api/inspections/", json=inspection_data)
    inspection_id = inspection_response.json()["id"]
    
    # For testing GET endpoint, we can mock a photo record in the database
    # In a real test with file uploads, this would be different
    from app.models.models import InspectionPhoto
    from app.db.database import get_db
    
    photo = InspectionPhoto(
        inspection_id=inspection_id,
        photo_path="/mock/path/photo.jpg",
        capture_date=date.today(),
        caption="Test Caption"
    )
    
    # Override the get_db dependency to access the test database directly
    db = next(client.app.dependency_overrides[get_db]())
    db.add(photo)
    db.commit()
    photo_id = photo.id
    
    # Get the photo
    response = client.get(f"/api/photos/{photo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == photo_id
    assert data["inspection_id"] == inspection_id
    assert data["photo_path"] == "/mock/path/photo.jpg"

def test_delete_photo(client):
    """Test deleting a photo via API"""
    # Create a project first
    project_data = {
        "name": "Test Project",
        "location": "Test Location",
        "contractor": "Test Contractor",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30))
    }
    create_response = client.post("/api/projects/", json=project_data)
    project_id = create_response.json()["id"]
    
    # Create an inspection
    inspection_data = {
        "project_id": project_id,
        "subproject_name": "Test Subproject",
        "inspection_form_name": "Test Form",
        "inspection_date": str(date.today()),
        "location": "Test Location",
        "timing": "檢驗停留點",
        "result": "合格",
        "remark": "Test remark"
    }
    inspection_response = client.post("/api/inspections/", json=inspection_data)
    inspection_id = inspection_response.json()["id"]
    
    # For testing DELETE endpoint, we can mock a photo record in the database
    from app.models.models import InspectionPhoto
    from app.db.database import get_db
    
    photo = InspectionPhoto(
        inspection_id=inspection_id,
        photo_path="/mock/path/photo.jpg",
        capture_date=date.today(),
        caption="Test Caption"
    )
    
    # Override the get_db dependency to access the test database directly
    db = next(client.app.dependency_overrides[get_db]())
    db.add(photo)
    db.commit()
    photo_id = photo.id
    
    # Delete the photo
    response = client.delete(f"/api/photos/{photo_id}")
    assert response.status_code == 200
    
    # Verify it's deleted
    response = client.get(f"/api/photos/{photo_id}")
    assert response.status_code == 404

# Add tests for error handling
def test_get_nonexistent_project(client):
    """Test getting a non-existent project"""
    response = client.get("/api/projects/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"

def test_get_nonexistent_inspection(client):
    """Test getting a non-existent inspection"""
    response = client.get("/api/inspections/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Inspection not found"

def test_get_nonexistent_photo(client):
    """Test getting a non-existent photo"""
    response = client.get("/api/photos/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Photo not found"

# Test validation errors
def test_create_project_validation_error(client):
    """Test creating a project with invalid data"""
    # Missing required fields
    project_data = {
        "name": "Test Project",
        # Missing location
        "contractor": "Test Contractor",
        # Missing dates
    }
    
    response = client.post("/api/projects/", json=project_data)
    assert response.status_code == 422  # Unprocessable Entity

def test_create_inspection_validation_error(client):
    """Test creating an inspection with invalid data"""
    # Missing required fields
    inspection_data = {
        # Missing project_id
        "subproject_name": "Test Subproject",
        # Missing other fields
    }
    
    response = client.post("/api/inspections/", json=inspection_data)
    assert response.status_code == 422  # Unprocessable Entity
