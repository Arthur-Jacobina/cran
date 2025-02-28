from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ...crud import user as user_crud
from ...app import get_db
from ..schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # print(user)
    # # Check if wallet address exists
    # db_user = user_crud.get_user(db, user.wallet_address)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Wallet address already registered")
    
    # # Check if username exists
    # db_user = user_crud.get_user_by_username(db, user.username)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Username already registered")
    
    # # Check if twitter handle exists
    # twitter_user = user_crud.get_user_by_twitter(db, user.twitter_handle)
    # if twitter_user:
    #     raise HTTPException(status_code=400, detail="Twitter handle already registered")
    
    return user_crud.create_user(db, user.dict())

@router.get("/{address}", response_model=UserResponse)
def read_user(address: str, db: Session = Depends(get_db)):
    try:
        # Normalize the address to lowercase or checksum format if needed
        normalized_address = address.lower()  # or Web3.toChecksumAddress(address)
        
        # Add debug logging
        print(f"Looking up user with address: {normalized_address}")
        
        db_user = user_crud.get_user(db, normalized_address)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
    except Exception as e:
        # Log the actual exception for debugging
        import traceback
        print(f"Error retrieving user: {str(e)}")
        print(traceback.format_exc())
        
        raise HTTPException(
            status_code=500,
            detail=f"Database error occurred: {str(e)}"
        )

@router.get("/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return user_crud.get_users(db, skip=skip, limit=limit)

@router.put("/{address}", response_model=UserResponse)
def update_user(address: str, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = user_crud.update_user(db, address, user.dict(exclude_unset=True))
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/{address}")
def delete_user(address: str, db: Session = Depends(get_db)):
    success = user_crud.delete_user(db, address)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"} 