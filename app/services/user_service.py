from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import User, FloorAddress
from app.schemas import UserUpdate, AddressCreate, AddressUpdate

async def get_user_by_id(db: AsyncSession, user_id: str):
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def update_user(db: AsyncSession, db_user: User, user_update: UserUpdate):
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user_addresses(db: AsyncSession, user_id: str):
    result = await db.execute(select(FloorAddress).filter(FloorAddress.user_id == user_id))
    return result.scalars().all()

async def create_address(db: AsyncSession, user_id: str, address: AddressCreate):
    if address.is_default:
        await reset_default_address(db, user_id)
    db_address = FloorAddress(**address.model_dump(), user_id=user_id)
    db.add(db_address)
    await db.commit()
    await db.refresh(db_address)
    return db_address

async def update_address(db: AsyncSession, user_id: str, address_id: str, address_update: AddressUpdate):
    result = await db.execute(select(FloorAddress).filter(FloorAddress.id == address_id, FloorAddress.user_id == user_id))
    db_address = result.scalars().first()
    if not db_address:
        return None
    if address_update.is_default:
        await reset_default_address(db, user_id)
    update_data = address_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_address, key, value)
    await db.commit()
    await db.refresh(db_address)
    return db_address

async def delete_address(db: AsyncSession, user_id: str, address_id: str):
    result = await db.execute(select(FloorAddress).filter(FloorAddress.id == address_id, FloorAddress.user_id == user_id))
    db_address = result.scalars().first()
    if not db_address:
        return False
    await db.delete(db_address)
    await db.commit()
    return True

async def reset_default_address(db: AsyncSession, user_id: str):
    addresses = await get_user_addresses(db, user_id)
    for addr in addresses:
        if addr.is_default:
            addr.is_default = False
    await db.commit()
