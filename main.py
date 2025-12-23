from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import psycopg2
import os

DATABASE_URL = os.environ["DATABASE_URL"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for MVP
    allow_methods=["*"],
    allow_headers=["*"],
)

class WaitlistEntry(BaseModel):
    email: EmailStr
    feedback: str | None = None
    _source: str | None = None

def get_conn():
    return psycopg2.connect(DATABASE_URL)

@app.post("/waitlist")
def add_to_waitlist(entry: WaitlistEntry):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO waitlist (email, feedback, source)
            VALUES (%s, %s, %s)
            ON CONFLICT (email) DO NOTHING
            """,
            (entry.email, entry.feedback, entry._source),
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

    return {"ok": True}
