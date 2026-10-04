from typing import Generator, List, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.models.audit import ActivityLog

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Validate JWT access token and return current authenticated User model."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception
    
    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
        
    return user


def require_role(allowed_roles: List[str]):
    """Enforce Role-Based Access Control (RBAC) on endpoints."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: requires one of the following roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker


def record_audit_log(
    db: Session,
    action: str,
    user_id: Optional[str] = None,
    agent: Optional[str] = None,
    workflow_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    result_status: str = "SUCCESS"
):
    """Utility to record immutable audit trail entries."""
    log = ActivityLog(
        user_id=user_id,
        action=action,
        agent=agent,
        workflow_id=workflow_id,
        details=details or {},
        ip_address=ip_address,
        result_status=result_status
    )
    db.add(log)
    db.commit()
