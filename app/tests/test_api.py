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

def test_update_inspection_preserve_pdf_path(client):
    """Test that pdf_path is preserved when not included in the update request"""
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
    
    # Create an inspection with a pdf_path
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
    
    # Set a pdf_path for the inspection
    update_with_pdf = {
        "result": "合格",
        "remark": "With PDF",
        "pdf_path": "/path/to/original/pdf"
    }
    response = client.put(f"/api/inspections/{inspection_id}", json=update_with_pdf)
    assert response.status_code == 200
    data = response.json()
    assert data["pdf_path"] == "/path/to/original/pdf"
    
    # Now update without including pdf_path
    update_without_pdf = {
        "result": "不合格",
        "remark": "Updated without PDF path"
    }
    
    response = client.put(f"/api/inspections/{inspection_id}", json=update_without_pdf)
    assert response.status_code == 200
    data = response.json()
    
    # Verify that the pdf_path is still preserved
    assert data["result"] == "不合格"
    assert data["remark"] == "Updated without PDF path"
    assert data["pdf_path"] == "/path/to/original/pdf", "pdf_path should not be changed when not included in update"

def test_delete_inspection(client):
    """Test deleting an inspection via API"""
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
    
    # Delete the inspection
    response = client.delete(f"/api/inspections/{inspection_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == inspection_id
    
    # Verify the inspection was deleted
    response = client.get(f"/api/inspections/{inspection_id}")
    assert response.status_code == 404

def test_delete_spot_check(client):
    """Test deleting a spot check inspection via API"""
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
    
    # Create a spot check inspection
    spot_check_data = {
        "project_id": project_id,
        "subproject_name": "Test Subproject",
        "inspection_form_name": "Spot Check Form",
        "inspection_date": str(date.today()),
        "location": "Test Location",
        "timing": "隨機抽查",  # This is a spot check
        "result": "合格",
        "remark": "Spot check remark"
    }
    
    create_response = client.post("/api/inspections/", json=spot_check_data)
    assert create_response.status_code == 201
    spot_check_id = create_response.json()["id"]
    
    # Verify the spot check was created
    response = client.get(f"/api/inspections/{spot_check_id}")
    assert response.status_code == 200
    assert response.json()["timing"] == "隨機抽查"
    
    # Add photos to the spot check
    from app.models.models import InspectionPhoto
    from app.db.database import get_db
    
    # Create multiple photos for the spot check
    photo1 = InspectionPhoto(
        inspection_id=spot_check_id,
        photo_path="/mock/path/photo1.jpg",
        capture_date=date.today(),
        caption="Spot Check Photo 1"
    )
    
    photo2 = InspectionPhoto(
        inspection_id=spot_check_id,
        photo_path="/mock/path/photo2.jpg",
        capture_date=date.today(),
        caption="Spot Check Photo 2"
    )
    
    # Add photos to the database
    db = next(client.app.dependency_overrides[get_db]())
    db.add(photo1)
    db.add(photo2)
    db.commit()
    photo1_id = photo1.id
    photo2_id = photo2.id
    
    # Verify photos were added
    response = client.get(f"/api/photos/?inspection_id={spot_check_id}")
    assert response.status_code == 200
    photos_data = response.json()
    assert len(photos_data) == 2
    
    # Delete the spot check
    delete_response = client.delete(f"/api/inspections/{spot_check_id}")
    assert delete_response.status_code == 200
    deleted_data = delete_response.json()
    assert deleted_data["id"] == spot_check_id
    assert deleted_data["timing"] == "隨機抽查"
    
    # Verify the spot check was deleted
    response = client.get(f"/api/inspections/{spot_check_id}")
    assert response.status_code == 404
    
    # Verify that all associated photos were also deleted
    response = client.get(f"/api/photos/{photo1_id}")
    assert response.status_code == 404
    
    response = client.get(f"/api/photos/{photo2_id}")
    assert response.status_code == 404
    
    # Verify no photos are returned when querying by the deleted inspection_id
    response = client.get(f"/api/photos/?inspection_id={spot_check_id}")
    assert response.status_code == 200
    assert len(response.json()) == 0

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

def test_patch_photo_caption_and_date(client):
    """Test partial update (PATCH) of photo caption and date only"""
    # 先建立一個 project 與 inspection
    project_data = {
        "name": "Patch Photo Project",
        "location": "Taipei",
        "contractor": "Test",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30))
    }
    project_resp = client.post("/api/projects/", json=project_data)
    assert project_resp.status_code == 201
    project_id = project_resp.json()["id"]
    
    inspection_data = {
        "project_id": project_id,
        "subproject_name": "Sub Project",
        "inspection_form_name": "Form Name",
        "inspection_date": str(date.today()),
        "location": "Location",
        "timing": "morning",
        "result": "合格",
        "remark": "Test remark"
    }
    inspection_resp = client.post("/api/inspections/", json=inspection_data)
    assert inspection_resp.status_code == 201
    inspection_id = inspection_resp.json()["id"]
    
    # 建立照片（需使用 multipart/form-data 上傳 file）
    import io
    photo_bytes = io.BytesIO(b"fake image content")
    photo_data = {
        "inspection_id": str(inspection_id),
        "capture_date": str(date.today()),
        "caption": "Original Caption"
    }
    files = {
        "file": ("photo.jpg", photo_bytes, "image/jpeg")
    }
    photo_resp = client.post("/api/photos/", data=photo_data, files=files)
    assert photo_resp.status_code == 201
    photo_id = photo_resp.json()["id"]
    
    # 確認照片已建立
    get_resp = client.get(f"/api/photos/{photo_id}")
    assert get_resp.status_code == 200
    
    # PATCH 只更新日期和描述
    new_date = str(date.today() + timedelta(days=1))
    patch_data = {
        "capture_date": new_date,
        "caption": "Updated Caption"
    }
    patch_resp = client.patch(f"/api/photos/{photo_id}", json=patch_data)
    assert patch_resp.status_code == 200
    patched = patch_resp.json()
    
    # 驗證只有指定欄位被更新
    assert patched["caption"] == "Updated Caption"
    assert patched["capture_date"] == new_date
    assert patched["inspection_id"] == inspection_id

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
