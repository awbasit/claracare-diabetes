import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.enums import UserRole
from app.models.patient import Patient
from app.models.user import User


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await db.get(User, user_id)


async def get_user_by_subject(db: AsyncSession, subject: str | None) -> User | None:
    if subject is None:
        return None
    try:
        user_id = uuid.UUID(subject)
    except ValueError:
        return None
    return await get_user_by_id(db, user_id)


async def create_user(
    db: AsyncSession, *, email: str, password: str, role: UserRole = UserRole.patient
) -> User:
    user = User(email=email, hashed_password=hash_password(password), role=role)
    db.add(user)
    await db.flush()

    if role == UserRole.patient:
        # Patient-role accounts need a Patient row to exist so get_current_patient can resolve one.
        db.add(Patient(user_id=user.id))

    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


async def get_patient_by_user_id(db: AsyncSession, user_id: uuid.UUID) -> Patient | None:
    result = await db.execute(select(Patient).where(Patient.user_id == user_id))
    return result.scalar_one_or_none()
