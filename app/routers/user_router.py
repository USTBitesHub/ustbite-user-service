from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.dependencies import get_user_headers
from app.schemas import UserResponse, UserUpdate, AddressResponse, AddressCreate, AddressUpdate
from app.services import user_service
from app.events.publisher import publish_event

router = APIRouter(prefix="/users/me", tags=["Users"])

def format_response(data, message="Success"):
    return {"data": data, "message": message, "status": "success"}

@router.get("", response_model=dict)
async def get_me(db: AsyncSession = Depends(get_db), headers: dict = Depends(get_user_headers)):
    email = headers.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Missing X-User-Email header")
    user = await user_service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return format_response(UserResponse.model_validate(user).model_dump(mode="json"))

@router.put("", response_model=dict)
async def update_me(user_update: UserUpdate, db: AsyncSession = Depends(get_db), headers: dict = Depends(get_user_headers)):
    email = headers.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Missing X-User-Email header")
    user = await user_service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = await user_service.update_user(db, user, user_update)
    
    # Publish event
    await publish_event("user.profile_updated", {
        "user_id": str(updated_user.id),
        "email": updated_user.email,
        "name": updated_user.name
    })
    
    return format_response(UserResponse.model_validate(updated_user).model_dump(mode="json"), "User updated successfully")

@router.get("/addresses", response_model=dict)
async def get_my_addresses(db: AsyncSession = Depends(get_db), headers: dict = Depends(get_user_headers)):
    email = headers.get("email")
    user = await user_service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    addresses = await user_service.get_user_addresses(db, user.id)
    return format_response([AddressResponse.model_validate(a).model_dump(mode="json") for a in addresses])

@router.post("/addresses", response_model=dict)
async def create_my_address(address: AddressCreate, db: AsyncSession = Depends(get_db), headers: dict = Depends(get_user_headers)):
    email = headers.get("email")
    user = await user_service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_address = await user_service.create_address(db, user.id, address)
    return format_response(AddressResponse.model_validate(new_address).model_dump(mode="json"), "Address created successfully")

@router.put("/addresses/{id}", response_model=dict)
async def update_my_address(id: str, address: AddressUpdate, db: AsyncSession = Depends(get_db), headers: dict = Depends(get_user_headers)):
    email = headers.get("email")
    user = await user_service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updated = await user_service.update_address(db, user.id, id, address)
    if not updated:
        raise HTTPException(status_code=404, detail="Address not found")
    return format_response(AddressResponse.model_validate(updated).model_dump(mode="json"), "Address updated successfully")

@router.delete("/addresses/{id}", response_model=dict)
async def delete_my_address(id: str, db: AsyncSession = Depends(get_db), headers: dict = Depends(get_user_headers)):
    email = headers.get("email")
    user = await user_service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    deleted = await user_service.delete_address(db, user.id, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Address not found")
    return format_response(None, "Address deleted successfully")
