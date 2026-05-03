from pydantic import BaseModel, ConfigDict, Field

# Dữ liệu Frontend gửi lên khi đăng ký
class UserCreate(BaseModel):
    email: str
    password: str = Field(..., min_length=6, max_length=50, description="Mật khẩu tối đa 50 ký tự")
    full_name: str

# Dữ liệu Backend trả về (Giấu password đi)
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
    
class UserLogin(BaseModel):
    email: str
    password: str = Field(..., max_length=50) # Nhớ chặn cả ở lúc Login

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"