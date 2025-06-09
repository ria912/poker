# aip/auth.py(Ver.0.0)
# ログイン機能関連コード
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# 仮のユーザーDB
fake_users_db = {
    "alice": {
        "username": "alice",
        "hashed_password": pwd_context.hash("secret123"),
    }
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    return fake_users_db.get(username)

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="ユーザー名が違います")
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="パスワードが違います")

    token = f"fake-token-for-{user['username']}"
    return {"access_token": token, "token_type": "bearer"}

@router.get("/secret")
def read_secret(token: str = Depends(oauth2_scheme)):
    if not token.startswith("fake-token-for-"):
        raise HTTPException(status_code=401, detail="無効なトークン")
    return {"message": "これは秘密のデータです！"}