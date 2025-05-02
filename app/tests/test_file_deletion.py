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
from app.tests.conftest import TEST_PDF_DIR, TEST_PHOTO_DIR, test_project, test_inspection, mock_pdf_path, mock_photo_path

client = TestClient(app)

# 獲取TestClient使用的測試資料庫會話
def get_test_db():
    """獲取測試使用的資料庫會話"""
    # 檢查是否有依賴覆蓋
    if hasattr(client.app, "dependency_overrides") and get_db in client.app.dependency_overrides:
        db = next(client.app.dependency_overrides[get_db]())
    else:
        db = next(get_db())
    return db

def test_delete_photo_with_file(client, test_project, test_inspection, mock_photo_path):
    """測試刪除照片時是否同時刪除實體檔案"""
    # 獲取測試資料庫連接
    db = get_test_db()
    
    # 使用 fixture 創建的測試數據
    photo = InspectionPhoto(
        inspection_id=test_inspection.id,
        photo_path=mock_photo_path,
        capture_date=date.today(),
        caption="Test Caption"
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    
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

def test_delete_inspection_with_pdf(client, test_project, mock_pdf_path):
    """測試刪除抽查時是否同時刪除 PDF 檔案"""
    # 獲取測試資料庫連接
    db = get_test_db()
    
    # 創建測試數據
    inspection = ConstructionInspection(
        project_id=test_project.id,
        subproject_name="Test Subproject",
        inspection_form_name="Test Form",
        inspection_date=date.today(),
        location="Test Location",
        timing="檢驗停留點",
        result="合格",
        remark="Test remark",
        pdf_path=mock_pdf_path
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    
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

def test_delete_inspection_with_photos(client, test_project, mock_pdf_path, mock_photo_path):
    """測試刪除抽查時是否同時刪除相關的照片檔案"""
    # 獲取測試資料庫連接
    db = get_test_db()
    
    # 創建測試數據
    inspection = ConstructionInspection(
        project_id=test_project.id,
        subproject_name="Test Subproject",
        inspection_form_name="Test Form",
        inspection_date=date.today(),
        location="Test Location",
        timing="檢驗停留點",
        result="合格",
        remark="Test remark",
        pdf_path=mock_pdf_path
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    
    photo = InspectionPhoto(
        inspection_id=inspection.id,
        photo_path=mock_photo_path,
        capture_date=date.today(),
        caption="Test Caption"
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    
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

def test_delete_project_cascade(client, test_project, mock_pdf_path, mock_photo_path):
    """測試刪除專案時是否級聯刪除所有相關的抽查和照片檔案"""
    # 獲取測試資料庫連接
    db = get_test_db()
    
    # 創建測試數據
    inspection = ConstructionInspection(
        project_id=test_project.id,
        subproject_name="Test Subproject",
        inspection_form_name="Test Form",
        inspection_date=date.today(),
        location="Test Location",
        timing="檢驗停留點",
        result="合格",
        remark="Test remark",
        pdf_path=mock_pdf_path
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    
    photo = InspectionPhoto(
        inspection_id=inspection.id,
        photo_path=mock_photo_path,
        capture_date=date.today(),
        caption="Test Caption"
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    
    # 確認檔案存在
    assert os.path.exists(mock_pdf_path), "測試 PDF 檔案應該存在"
    assert os.path.exists(mock_photo_path), "測試照片檔案應該存在"
    
    # 刪除專案
    response = client.delete(f"/api/projects/{test_project.id}")
    assert response.status_code == 200, "刪除專案應該成功"
    
    # 確認資料庫記錄已刪除
    response = client.get(f"/api/projects/{test_project.id}")
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

def test_update_inspection_replace_pdf(client, test_project, mock_pdf_path):
    """測試更新抽查的 PDF 路徑時是否刪除舊檔案"""
    # 創建一個新的 PDF 檔案路徑
    new_pdf_path = os.path.join(TEST_PDF_DIR, "new_inspection.pdf")
    with open(new_pdf_path, "wb") as f:
        f.write(b"New PDF content")
    
    # 獲取測試資料庫連接
    db = get_test_db()
    
    # 創建測試數據
    inspection = ConstructionInspection(
        project_id=test_project.id,
        subproject_name="Test Subproject",
        inspection_form_name="Test Form",
        inspection_date=date.today(),
        location="Test Location",
        timing="檢驗停留點",
        result="合格",
        remark="Test remark",
        pdf_path=mock_pdf_path
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    
    # 確認舊檔案存在
    assert os.path.exists(mock_pdf_path), "測試 PDF 檔案應該存在"
    
    # 更新抽查
    update_data = {
        "result": "合格",  # 需要提供必填欄位
        "pdf_path": new_pdf_path
    }
    response = client.put(f"/api/inspections/{inspection.id}", json=update_data)
    assert response.status_code == 200, "更新抽查應該成功"
    
    # 確認舊檔案已刪除
    assert not os.path.exists(mock_pdf_path), "舊的 PDF 檔案應該已被刪除"
    
    # 清理新檔案
    if os.path.exists(new_pdf_path):
        os.remove(new_pdf_path)

def test_update_photo_replace_file(client, test_project, test_inspection, mock_photo_path):
    """測試更新照片路徑時是否刪除舊檔案"""
    # 創建一個新的照片檔案路徑
    new_photo_path = os.path.join(TEST_PHOTO_DIR, "new_photo.jpg")
    with open(new_photo_path, "wb") as f:
        f.write(b"New photo content")
    
    # 獲取測試資料庫連接
    db = get_test_db()
    
    # 創建測試數據
    photo = InspectionPhoto(
        inspection_id=test_inspection.id,
        photo_path=mock_photo_path,
        capture_date=date.today(),
        caption="Test Caption"
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    
    # 確認舊檔案存在
    assert os.path.exists(mock_photo_path), "測試照片檔案應該存在"
    
    # 更新照片
    update_data = {
        "photo_path": new_photo_path
    }
    response = client.put(f"/api/photos/{photo.id}", json=update_data)
    assert response.status_code == 200, "更新照片應該成功"
    
    # 確認舊檔案已刪除
    assert not os.path.exists(mock_photo_path), "舊的照片檔案應該已被刪除"
    
    # 清理新檔案
    if os.path.exists(new_photo_path):
        os.remove(new_photo_path)

def test_error_handling_when_file_not_exists(client, test_project, test_inspection):
    """測試當檔案不存在時的錯誤處理"""
    # 獲取測試資料庫連接
    db = get_test_db()
    
    # 創建一個不存在的檔案路徑
    non_existent_path = os.path.join(TEST_PDF_DIR, "non_existent.pdf")
    
    # 創建測試數據
    inspection = ConstructionInspection(
        project_id=test_project.id,
        subproject_name="Test Subproject",
        inspection_form_name="Test Form",
        inspection_date=date.today(),
        location="Test Location",
        timing="檢驗停留點",
        result="合格",
        remark="Test remark",
        pdf_path=non_existent_path
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    
    # 刪除抽查，即使檔案不存在也應該成功
    response = client.delete(f"/api/inspections/{inspection.id}")
    assert response.status_code == 200, "即使檔案不存在，刪除抽查也應該成功"
