import uuid
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import enum

class DepartmentEnum(str, enum.Enum):
    IT = "IT"
    HR = "HR"
    Finance = "Finance"
    Operations = "Operations"
    Design = "Design"
    Management = "Management"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String)
    department = Column(String, nullable=False)          # stored as VARCHAR; enum enforced in app layer
    floor_number = Column(String)
    password_hash = Column(String, nullable=True)        # bcrypt hash; nullable for backwards compat
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class FloorAddress(Base):
    __tablename__ = "floor_addresses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    label = Column(String, nullable=False)
    floor_number = Column(String, nullable=False)
    wing = Column(String)
    building = Column(String)
    is_default = Column(Boolean, default=False)
