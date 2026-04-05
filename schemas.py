from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)

    
class UserOut(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True