from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.models import DepartmentEnum

class AddressBase(BaseModel):
    label: str
    floor_number: str
    wing: Optional[str] = None
    building: Optional[str] = None
    is_default: bool = False

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseModel):
    label: Optional[str] = None
    floor_number: Optional[str] = None
    wing: Optional[str] = None
    building: Optional[str] = None
    is_default: Optional[bool] = None

class AddressResponse(AddressBase):
    id: UUID
    user_id: UUID
    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    name: str
    phone: Optional[str] = None
    department: DepartmentEnum
    floor_number: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[DepartmentEnum] = None
    floor_number: Optional[str] = None

class UserResponse(UserBase):
    id: UUID
    employee_id: str
    email: EmailStr
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class StandardResponse(BaseModel):
    data: Optional[dict] = None
    message: str
    status: str
