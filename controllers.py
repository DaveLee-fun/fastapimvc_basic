from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from models import User, Memo  # 모델 import
from schemas import UserCreate, UserLogin, MemoCreate, MemoUpdate  # 스키마 import
from dependencies import get_db, get_password_hash, verify_password  # 의존성 import
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/signup")
async def signup(signup_data: UserCreate, db: Session = Depends(get_db)):
    # 먼저 username이 이미 존재하는지 확인
    existing_user = db.query(User).filter(User.username == signup_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 동일 사용자 이름이 가입되어 있습니다.")
    hashed_password = get_password_hash(signup_data.password)
    new_user = User(username=signup_data.username, email=signup_data.email, hashed_password=hashed_password)
    db.add(new_user)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()  # 에러 발생 시 롤백
        raise HTTPException(status_code=500, detail="회원가입이 실패했습니다. 기입한 내용을 확인해보세요")

    db.refresh(new_user)
    return {"message": "회원가입을 성공했습니다"}


@router.post("/login")
async def login(request: Request, signin_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == signin_data.username).first()
    if user and verify_password(signin_data.password, user.hashed_password):
        request.session["username"] = user.username
        return {"message": "Logged in successfully"}
    else:
        # "Unauthorized" 메시지 대신 사용자에게 더 명확한 메시지를 제공합니다.
        raise HTTPException(status_code=401, detail="로그인을 실패했습니다.")
    

@router.post("/logout")
async def logout(request: Request):
    request.session.pop("username", None)
    return {"message": "Logged out successfully"}


@router.post("/memos/")
async def create_user(request: Request, memo: MemoCreate, db: Session = Depends(get_db)):
    username = request.session.get("username")
    if username is None:
        raise HTTPException(status_code=401, detail="Not authorized")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")    
    new_memo = Memo(user_id=user.id, title=memo.title, content=memo.content)
    db.add(new_memo)
    db.commit()
    db.refresh(new_memo) 
    return new_memo


@router.get("/memos/")
async def list_memos(request: Request, db: Session = Depends(get_db)):
    username = request.session.get("username")
    if username is None:
        raise HTTPException(status_code=401, detail="Not authorized")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")                
    memos = db.query(Memo).filter(Memo.user_id == user.id).all()
    return templates.TemplateResponse("memos.html", {
        "request": request, 
        "memos": memos, 
        "username": username  # 사용자 이름을 컨텍스트에 추가
    })
    

@router.put("/memos/{memo_id}")
async def update_user(request: Request, memo_id: int, memo: MemoUpdate, db: Session = Depends(get_db)):
    username = request.session.get("username")
    if username is None:
        raise HTTPException(status_code=401, detail="Not authorized")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")    
    db_memo = db.query(Memo).filter(Memo.id == memo_id, Memo.user_id == user.id).first()
    if db_memo is None:
        return {"error": "User not found"}
    
    if memo.title is not None:
        db_memo.title = memo.title
    if memo.content is not None:
        db_memo.content = memo.content

    db.commit()
    db.refresh(db_memo)
    return db_memo


@router.delete("/memos/{memo_id}")
async def delete_user(request: Request, memo_id: int, db: Session = Depends(get_db)):
    username = request.session.get("username")
    if username is None:
        raise HTTPException(status_code=401, detail="Not authorized")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")    
    db_memo = db.query(Memo).filter(Memo.id == memo_id, Memo.user_id == user.id).first()
    if db_memo is None:
        return {"error": "Memo not found"}
    db.delete(db_memo)
    db.commit()
    return {"message": "Memo deleted"}


@router.get('/')
async def read_root(request: Request):
    return templates.TemplateResponse('home.html', {"request": request})


@router.get('/about')
async def about():
    return {"message": "이것은 마이 메모 앱의 소개 페이지입니다."}
