from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import service
from app.core.security import decode_token
from app.database.session import get_db
from app.models.patient import Patient
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise credentials_exception
    try:
        payload = decode_token(credentials.credentials)
    except JWTError as err:
        raise credentials_exception from err
    if payload.get("type") != "access":
        raise credentials_exception
    user = await service.get_user_by_subject(db, payload.get("sub"))
    if user is None or not user.is_active:
        raise credentials_exception
    return user


async def get_current_patient(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Patient:
    patient = await service.get_patient_by_user_id(db, user.id)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found for this user",
        )
    return patient
