import os
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

# Khởi tạo CryptContext (chuyển từ main.py sang đây)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("JWT_SECRET", "default_secret_key_if_env_is_missing")
ALGORITHM = "HS256"

def verify_password(plain_password, hashed_password):
    """Kiểm tra mật khẩu người dùng nhập có khớp với hash trong DB không"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Băm mật khẩu"""
    return pwd_context.hash(password)

def create_access_token(data: dict):
    """Tạo JWT Token"""
    to_encode = data.copy()
    expire_minutes = int(os.getenv("JWT_EXPIRATION_MINUTES", 60))
    # Token sẽ hết hạn sau 60 phút
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt