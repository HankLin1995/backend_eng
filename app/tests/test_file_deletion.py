import pytest
import os
import shutil
from fastapi.testclient import TestClient
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
from app.main import app
from app.db.database import get_db
from app.models.models import Project, ConstructionInspection, InspectionPhoto
from app.utils.file_utils import PDF_UPLOAD_DIR, PHOTO_UPLOAD_DIR

client = TestClient(app)

# 設置測試用的上傳目錄
TEST_PDF_DIR = "app/static/test_uploads/pdfs"
TEST_PHOTO_DIR = "app/static/test_uploads/photos"

@pytest.fixture(scope="module", autouse=True)
def setup_test_dirs():
    """設置測試目錄並在測試結束後清理"""
    # 創建測試目錄
    os.makedirs(TEST_PDF_DIR, exist_ok=True)
    os.makedirs(TEST_PHOTO_DIR, exist_ok=True)
    
    yield
    
    # 清理測試目錄
    if os.path.exists(TEST_PDF_DIR):
        shutil.rmtree(TEST_PDF_DIR)
    if os.path.exists(TEST_PHOTO_DIR):
        shutil.rmtree(TEST_PHOTO_DIR)

@pytest.fixture
def mock_pdf_path():
    """創建一個測試用的 PDF 檔案並返回路徑"""
    pdf_path = os.path.join(TEST_PDF_DIR, "test_inspection.pdf")
    
    # 創建一個空的 PDF 檔案
    with open(pdf_path, "wb") as f:
        f.write(b"Test PDF content")
    
    yield pdf_path
    
    # 測試後清理（如果檔案還存在）
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

@pytest.fixture
def mock_photo_path():
    """創建一個測試用的照片檔案並返回路徑"""
    photo_path = os.path.join(TEST_PHOTO_DIR, "test_photo.jpg")
    
    # 創建一個空的照片檔案
    with open(photo_path, "wb") as f:
        f.write(b"Test photo content")
    
    yield photo_path
    
    # 測試後清理（如果檔案還存在）
    if os.path.exists(photo_path):
        os.remove(photo_path)

# 獲取TestClient使用的測試資料庫會話
def get_test_db():
    """獲取測試使用的資料庫會話"""
    # 檢查是否有依賴覆蓋
    if hasattr(client.app, "dependency_overrides") and get_db in client.app.dependency_overrides:
        db = next(client.app.dependency_overrides[get_db]())
    else:
        db = next(get_db())
    return db

def create_test_project(db):
    """創建一個測試用的專案"""
    project = Project(
        name="Test Project",
        location="Test Location",
        contractor="Test Contractor",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def create_test_inspection(db, project_id, pdf_path=None):
    """創建一個測試用的抽查"""
    inspection = ConstructionInspection(
        project_id=project_id,
        subproject_name="Test Subproject",
        inspection_form_name="Test Form",
        inspection_date=date.today(),
        location="Test Location",
        timing="檢驗停留點",
        result="合格",
        remark="Test remark",
        pdf_path=pdf_path
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    return inspection

def create_test_photo(db, inspection_id, photo_path):
    """創建一個測試用的照片"""
    photo = InspectionPhoto(
        inspection_id=inspection_id,
        photo_path=photo_path,
        capture_date=date.today(),
        caption="Test Caption"
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo

def test_delete_photo_with_file(client, mock_photo_path):
    """測試刪除照片時是否同時刪除實體檔案"""
    # 獲取測試資料庫連接
    db = get_test_db()
    
    # 創建測試數據
    project = create_test_project(db)
    inspection = create_test_inspection(db, project.id)
    photo = create_test_photo(db, inspection.id, mock_photo_path)
    
    # 確認檔案存在
    assert os.path.exists(mock_photo_path), "測試照片檔案應該存在"
    
    # 刪除照片
    response = client.delete(f"/api/photos/{photo.id}")
    assert response.status_code == 200, "刪除照片應該成功"
    
    # 確認資料庫記錄已刪除
    response = client.get(f"/api/photos/{photo.id}")
    assert response.status_code == 404, "照片記錄應該已從資料庫中刪除"
    
    # 確認實體檔案已刪除
    assert not os.path.exists(mock_photo_path), "照片實體檔案應該已被刪除"

def test_delete_inspection_with_pdf(client, mock_pdf_path):
    """測試刪除抽查時是否同時刪除 PDF 檔案"""
    # 獲取測試資料庫連接
    db = get_test_db()
    
    # 創建測試數據
    project = create_test_project(db)
    inspection = create_test_inspection(db, project.id, mock_pdf_path)
    
    # 確認檔案存在
    assert os.path.exists(mock_pdf_path), "測試 PDF 檔案應該存在"
    
    # 刪除抽查
    response = client.delete(f"/api/inspections/{inspection.id}")
    assert response.status_code == 200, "刪除抽查應該成功"
    
    # 確認資料庫記錄已刪除
    response = client.get(f"/api/inspections/{inspection.id}")
    assert response.status_code == 404, "抽查記錄應該已從資料庫中刪除"
    
    # 確認實體檔案已刪除
    assert not os.path.exists(mock_pdf_path), "PDF 實體檔案應該已被刪除"

def test_delete_inspection_with_photos(client, mock_pdf_path, mock_photo_path):
    """測試刪除抽查時是否同時刪除相關的照片檔案"""
    # 獲取測試資料庫連接
    db = get_test_db()
    
    # 創建測試數據
    project = create_test_project(db)
    inspection = create_test_inspection(db, project.id, mock_pdf_path)
    photo = create_test_photo(db, inspection.id, mock_photo_path)
    
    # 確認檔案存在
    assert os.path.exists(mock_pdf_path), "測試 PDF 檔案應該存在"
    assert os.path.exists(mock_photo_path), "測試照片檔案應該存在"
    
    # 刪除抽查
    response = client.delete(f"/api/inspections/{inspection.id}")
    assert response.status_code == 200, "刪除抽查應該成功"
    
    # 確認資料庫記錄已刪除
    response = client.get(f"/api/inspections/{inspection.id}")
    assert response.status_code == 404, "抽查記錄應該已從資料庫中刪除"
    
    # 確認照片記錄已刪除
    response = client.get(f"/api/photos/{photo.id}")
    assert response.status_code == 404, "照片記錄應該已從資料庫中刪除"
    
    # 確認實體檔案已刪除
    assert not os.path.exists(mock_pdf_path), "PDF 實體檔案應該已被刪除"
    assert not os.path.exists(mock_photo_path), "照片實體檔案應該已被刪除"

def test_delete_project_cascade(client, mock_pdf_path, mock_photo_path):
    """測試刪除專案時是否級聯刪除所有相關的抽查和照片檔案"""
    # 獲取測試資料庫連接
    db = get_test_db()
    
    # 創建測試數據
    project = create_test_project(db)
    inspection = create_test_inspection(db, project.id, mock_pdf_path)
    photo = create_test_photo(db, inspection.id, mock_photo_path)
    
    # 確認檔案存在
    assert os.path.exists(mock_pdf_path), "測試 PDF 檔案應該存在"
    assert os.path.exists(mock_photo_path), "測試照片檔案應該存在"
    
    # 刪除專案
    response = client.delete(f"/api/projects/{project.id}")
    assert response.status_code == 200, "刪除專案應該成功"
    
    # 確認資料庫記錄已刪除
    response = client.get(f"/api/projects/{project.id}")
    assert response.status_code == 404, "專案記錄應該已從資料庫中刪除"
    
    # 確認抽查記錄已刪除
    response = client.get(f"/api/inspections/{inspection.id}")
    assert response.status_code == 404, "抽查記錄應該已從資料庫中刪除"
    
    # 確認照片記錄已刪除
    response = client.get(f"/api/photos/{photo.id}")
    assert response.status_code == 404, "照片記錄應該已從資料庫中刪除"
    
    # 確認實體檔案已刪除
    assert not os.path.exists(mock_pdf_path), "PDF 實體檔案應該已被刪除"
    assert not os.path.exists(mock_photo_path), "照片實體檔案應該已被刪除"

def test_update_inspection_replace_pdf(client, mock_pdf_path):
    """測試更新抽查的 PDF 路徑時是否刪除舊檔案"""
    # 獲取測試資料庫連接
    db = get_test_db()
    
    # 創建測試數據
    project = create_test_project(db)
    inspection = create_test_inspection(db, project.id)
    
    # 創建舊PDF檔案
    old_pdf_path = os.path.join(TEST_PDF_DIR, "old_test.pdf")
    with open(old_pdf_path, "wb") as f:
        f.write(b"Old PDF content")
    
    # 更新抽查的PDF路徑
    inspection.pdf_path = old_pdf_path
    db.commit()
    
    # 確認舊檔案存在
    assert os.path.exists(old_pdf_path), "舊 PDF 檔案應該存在"
    
    # 創建新檔案
    with open(mock_pdf_path, "wb") as f:
        f.write(b"New PDF content")
    
    # 更新抽查為新的PDF路徑
    update_data = {
        "result": inspection.result,
        "remark": inspection.remark,
        "pdf_path": mock_pdf_path
    }
    
    response = client.put(f"/api/inspections/{inspection.id}", json=update_data)
    assert response.status_code == 200, "更新抽查應該成功"
    
    # 確認舊檔案已刪除
    assert not os.path.exists(old_pdf_path), "舊 PDF 檔案應該已被刪除"
    
    # 確認新檔案存在
    assert os.path.exists(mock_pdf_path), "新 PDF 檔案應該存在"
    
    # 清理
    if os.path.exists(old_pdf_path):
        os.remove(old_pdf_path)

def test_update_photo_replace_file(client, mock_photo_path):
    """測試更新照片路徑時是否刪除舊檔案"""
    # 獲取測試資料庫連接
    db = get_test_db()
    
    # 創建測試數據
    project = create_test_project(db)
    inspection = create_test_inspection(db, project.id)
    
    # 創建舊照片檔案
    old_photo_path = os.path.join(TEST_PHOTO_DIR, "old_test_photo.jpg")
    with open(old_photo_path, "wb") as f:
        f.write(b"Old photo content")
    
    # 創建照片記錄
    photo = InspectionPhoto(
        inspection_id=inspection.id,
        photo_path=old_photo_path,
        capture_date=date.today(),
        caption="Test Caption"
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    
    # 確認舊檔案存在
    assert os.path.exists(old_photo_path), "舊照片檔案應該存在"
    
    # 創建新檔案
    with open(mock_photo_path, "wb") as f:
        f.write(b"New photo content")
    
    # 更新照片路徑
    update_data = {
        "photo_path": mock_photo_path,
        "capture_date": str(date.today()),
        "caption": "Updated Caption"
    }
    
    response = client.put(f"/api/photos/{photo.id}", json=update_data)
    assert response.status_code == 200, "更新照片應該成功"
    
    # 確認舊檔案已刪除
    assert not os.path.exists(old_photo_path), "舊照片檔案應該已被刪除"
    
    # 確認新檔案存在
    assert os.path.exists(mock_photo_path), "新照片檔案應該存在"
    
    # 清理
    if os.path.exists(old_photo_path):
        os.remove(old_photo_path)

def test_error_handling_when_file_not_exists(client):
    """測試當檔案不存在時的錯誤處理"""
    # 獲取測試資料庫連接
    db = get_test_db()
    
    # 創建測試數據，但使用不存在的檔案路徑
    project = create_test_project(db)
    non_existent_path = os.path.join(TEST_PDF_DIR, "non_existent.pdf")
    inspection = create_test_inspection(db, project.id, non_existent_path)
    
    # 刪除抽查，即使檔案不存在也應該成功
    response = client.delete(f"/api/inspections/{inspection.id}")
    assert response.status_code == 200, "即使檔案不存在，刪除抽查也應該成功"
    
    # 確認資料庫記錄已刪除
    response = client.get(f"/api/inspections/{inspection.id}")
    assert response.status_code == 404, "抽查記錄應該已從資料庫中刪除"
