# main.py

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine
import models, schemas
from auth import hash_password, verify_password, create_token

from fastapi.middleware.cors import CORSMiddleware

# create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= DB DEP =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ================= ROOT =================
@app.get("/")
def root():
    return {"message": "API running"}

# ================= REGISTER =================
@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    try:
        existing_user = db.query(models.User).filter(
            models.User.email == user.email
        ).first()

        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        new_user = models.User(
            username=user.username,
            email=user.email,
            password=hash_password(user.password)
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"message": "User registered successfully"}

    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
# ================= LOGIN =================
@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid password")

    token = create_token({"user_id": db_user.id})

    return {
        "token": token,
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email
        }
    }