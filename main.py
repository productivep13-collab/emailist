import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# =====================
# App
# =====================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
# Database
# =====================
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =====================
# Models
# =====================
class WaitlistEntry(BaseModel):
    email: EmailStr
    feedback: str | None = None
    source: str | None = None

# =====================
# Routes
# =====================
@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/waitlist")
def join_waitlist(data: WaitlistEntry, db: Session = Depends(get_db)):
    db.execute(
        text("""
            INSERT INTO waitlist (email, feedback, source)
            VALUES (:email, :feedback, :source)
        """),
        {
            "email": data.email,
            "feedback": data.feedback,
            "source": data.source,
        }
    )
    db.commit()
    return {"ok": True}
