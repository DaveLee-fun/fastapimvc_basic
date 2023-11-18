from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from database import Base 

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(200))
    hashed_password = Column(String(512))

class Memo(Base):
    __tablename__ = 'memo'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # 사용자 참조 추가    
    title = Column(String(100), nullable=False) # (nullable=False) 값이 없는 예외 경우 방지
    content = Column(String(1000), nullable=False) # (nullable=False) 값이 없는 예외 경우 방지
    
    user = relationship("User")  # 사용자와의 관계 설정
