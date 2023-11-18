from sqlalchemy.orm import Session
from passlib.context import CryptContext
from sqlalchemy.orm import Session, sessionmaker, relationship
from database import SessionLocal 

# 비밀번호 해싱을 위한 CryptContext 인스턴스 생성
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
