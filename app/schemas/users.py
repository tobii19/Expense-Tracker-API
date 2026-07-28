from pydantic import EmailStr,BaseModel, ConfigDict

class CreateUser(BaseModel):
    name : str
    email : EmailStr
    password : str
    
class UpdateUser(BaseModel):
    name : str
    email : str
    password : str

class UserResponse(BaseModel):
    name : str
    email : str
    
    class Config:
        from_attributes = True
        
class User(BaseModel):
    email : str
    password : str