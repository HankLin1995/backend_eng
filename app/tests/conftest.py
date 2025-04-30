import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.db.database import Base
from app.main import app
from app.db.database import get_db
import os
import sys

os.makedirs("app/data", exist_ok=True)  # <--- 加在這裡

# 使用記憶體資料庫來加速測試
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# 創建測試引擎和 session factory
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 只創建一次表格，提高測試速度
@pytest.fixture(scope="session")
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db(create_tables):
    # 連接到資料庫並開始事務
    connection = engine.connect()
    transaction = connection.begin()
    
    # 綁定 session 到這個連接
    session = TestingSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        # 回滾事務而不是刪除表格，這樣更快
        transaction.rollback()
        connection.close()

@pytest.fixture(scope="function")
def client(db):
    # 覆蓋 get_db 依賴項以使用測試資料庫
    def override_get_db():
        try:
            yield db
        finally:
            pass  # 不在這裡關閉，由 db fixture 處理
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # 重置依賴項覆蓋
    app.dependency_overrides = {}
