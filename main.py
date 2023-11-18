from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from controllers import router  # 컨트롤러 라우터 임포트
from database import Base, engine  # 데이터베이스 설정 임포트
from starlette.middleware.sessions import SessionMiddleware

# FastAPI 인스턴스 생성
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
templates = Jinja2Templates(directory="templates")

# 템플릿 디렉토리 설정
templates = Jinja2Templates(directory="templates")

# 라우터 포함
app.include_router(router)

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

@app.get('/')
async def read_root(request: Request):
    return templates.TemplateResponse('home.html', {"request": request})
