from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from .database import get_db
from .models import Student
from .security import get_password_hash, verify_password, create_access_token

app = FastAPI(title="Profile Service API")

# --- SCHEMAS ---
class StudentRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    province: str
    area_code: str

class StudentLogin(BaseModel):
    email: EmailStr
    password: str

# --- API ENDPOINTS ---

@app.post("/api/v1/auth/register")
def register_student(student_data: StudentRegister, db: Session = Depends(get_db)):
    existing_user = db.query(Student).filter(Student.email == student_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email đã tồn tại")
    
    # Dùng hàm hash từ file security.py
    hashed_pwd = get_password_hash(student_data.password)
    
    new_student = Student(
        full_name=student_data.full_name,
        email=student_data.email,
        password_hash=hashed_pwd,
        province=student_data.province,
        area_code=student_data.area_code
    )
    
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    # Sinh JWT Token thật
    access_token = create_access_token(data={"sub": str(new_student.student_id)})
    
    return {
        "student_id": new_student.student_id,
        "token": access_token
    }

@app.post("/api/v1/auth/login")
def login_student(login_data: StudentLogin, db: Session = Depends(get_db)):
    # 1. Tìm user bằng email
    user = db.query(Student).filter(Student.email == login_data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu sai") #[cite: 1]
    
    # 2. Kiểm tra mật khẩu
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu sai") #[cite: 1]
    
    # 3. Sinh JWT Token
    access_token = create_access_token(data={"sub": str(user.student_id)})
    
    # 4. Trả về đúng format tài liệu yêu cầu[cite: 1]
    return {
        "token": access_token,
        "student_id": user.student_id,
        "expires_in": 3600
    }