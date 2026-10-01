from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# 1. Setup Database (SQLite)
DATABASE_URL = "sqlite:///./smile_app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models na Database
class DBUser(Base):
    __tablename__ = "users"
    phone_number = Column(String, primary_key=True, index=True)
    status = Column(String, default="Ina amfani da Smile©️!")

class DBMessage(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sender = Column(String)
    receiver = Column(String)
    text = Column(String)

Base.metadata.create_all(bind=engine)

# 2. Setup FastAPI App
app = FastAPI(title="Smile©️ Messenger 2009 API")

# Ba wa Shashen Frontend damar shigowa (CORS Settings)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Yana barin kowane shafin HTML ya jona
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Samun damar Database Connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schemas
class UserRegistration(BaseModel):
    phone_number: str

class StatusUpdate(BaseModel):
    phone_number: str
    new_status: str

class MessageSend(BaseModel):
    sender: str
    receiver: str
    text_message: str

# --- ENDPOINTS / ROUTES ---

@app.get("/")
def home():
    return {"app": "Smile©️ Messenger", "status": "Online"}

@app.post("/register")
def register_user(user: UserRegistration, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.phone_number == user.phone_number).first()
    if db_user:
        return {"status": "Tuni kake da asusu", "user": {"phone_number": db_user.phone_number, "status": db_user.status}}
    
    new_user = DBUser(phone_number=user.phone_number)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "An yi rijista!", "user": {"phone_number": new_user.phone_number, "status": new_user.status}}

@app.put("/status")
def update_status(status_data: StatusUpdate, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.phone_number == status_data.phone_number).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Ba a sami wannan lambar ba")
    
    db_user.status = status_data.new_status
    db.commit()
    return {"message": "An sabunta!", "current_status": db_user.status}

@app.post("/send")
def send_message(msg: MessageSend, db: Session = Depends(get_db)):
    # Tabbatar mutanen biyu suna da asusu
    sender_exists = db.query(DBUser).filter(DBUser.phone_number == msg.sender).first()
    receiver_exists = db.query(DBUser).filter(DBUser.phone_number == msg.receiver).first()
    
    if not sender_exists or not receiver_exists:
        raise HTTPException(status_code=404, detail="Mai aikawa ko mai karba baya kan Smile©️")
    
    new_msg = DBMessage(sender=msg.sender, receiver=msg.receiver, text=msg.text_message)
    db.add(new_msg)
    db.commit()
    return {"status": "Saƙo ya tafi! 🚀"}

@app.get("/messages/{phone_number}")
def get_messages(phone_number: str, db: Session = Depends(get_db)):
    # Dauko saƙonnin da mutum ya karba ko ya tura
    messages = db.query(DBMessage).filter(
        (DBMessage.receiver == phone_number) | (DBMessage.sender == phone_number)
    ).all()
    return {"phone_number": phone_number, "inbox": messages}