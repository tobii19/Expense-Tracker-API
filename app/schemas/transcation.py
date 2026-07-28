from pydantic import BaseModel,EmailStr
from datetime import date
from typing import Optional

class Create_Transcaion(BaseModel):
    name : str
    type : str
    description : str
    date : Optional[date] = None
    amount : int
    
class Transaction_Response(BaseModel):
    id: int
    name: str     
    amount: float
    type: str
    description: str