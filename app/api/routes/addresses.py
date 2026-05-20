from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime, timezone
from pydantic import BaseModel, constr

from app.core.database import get_db
from app.models.address import Address
from app.core.security import get_current_user
from sqlalchemy.future import select
from sqlalchemy import update

router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"],
    responses={404: {"description": "Not found"}},
)

class AddressBase(BaseModel):
    full_name: str
    mobile: str
    street_address: str
    city: str
    state: str
    pincode: str
    is_default: bool = False

class AddressCreate(AddressBase):
    pass

class AddressResponse(AddressBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(
    address_data: AddressCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    if address_data.is_default:
        await db.execute(
            update(Address)
            .where(Address.user_id == user.id)
            .values(is_default=False)
        )
    else:
        result = await db.execute(select(Address).where(Address.user_id == user.id))
        if not result.scalars().first():
            address_data.is_default = True

    new_address = Address(
        user_id=user.id,
        **address_data.model_dump()
    )
    db.add(new_address)
    await db.commit()
    await db.refresh(new_address)
    return new_address

@router.get("/", response_model=List[AddressResponse])
async def get_my_addresses(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    result = await db.execute(
        select(Address).where(Address.user_id == user.id).order_by(Address.created_at.desc())
    )
    return result.scalars().all()

@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    result = await db.execute(select(Address).where(Address.id == address_id, Address.user_id == user.id))
    address = result.scalar_one_or_none()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
        
    await db.delete(address)
    
    # If the deleted address was default, make the most recent one default
    if address.is_default:
        result = await db.execute(
            select(Address).where(Address.user_id == user.id).order_by(Address.created_at.desc())
        )
        first_address = result.scalars().first()
        if first_address:
            first_address.is_default = True
            
    await db.commit()
    return None
