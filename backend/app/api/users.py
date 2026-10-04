from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role, record_audit_log
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users Management"])


@router.get("", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN.value]))
):
    """List all registered platform users (Admin only)."""
    return db.query(User).order_by(User.created_at.desc()).all()


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN.value]))
):
    """Update user role, status, or details (Admin only)."""
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if update_data.full_name is not None:
        target.full_name = update_data.full_name
    if update_data.role is not None:
        target.role = update_data.role
    if update_data.is_active is not None:
        target.is_active = update_data.is_active

    db.commit()
    db.refresh(target)

    record_audit_log(
        db,
        action="USER_UPDATED",
        user_id=current_user.id,
        details={"target_user_id": user_id, "new_role": target.role, "is_active": target.is_active}
    )
    return target
