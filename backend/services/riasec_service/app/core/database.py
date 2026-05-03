from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Khởi tạo kết nối DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency để sử dụng trong các API (tự động đóng kết nối khi xong request)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()