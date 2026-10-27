"""Tracko sync backend.  Run:  TRACKO_KEY=yoursecret uvicorn server:app --host 0.0.0.0 --port 8000
Deploy on Render / Railway / any VPS behind HTTPS (Android blocks plain http by default)."""
import json
import os
import sqlite3

from fastapi import FastAPI, Header, HTTPException

KEY = os.getenv("TRACKO_KEY", "change-me")
app = FastAPI()
db = sqlite3.connect(os.getenv("TRACKO_DB", "tracko_server.db"), check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS snap(user TEXT PRIMARY KEY, data TEXT)")


def auth(k):
    if k != KEY:
        raise HTTPException(401, "bad key")


@app.get("/sync/{user}")
def get(user: str, x_key: str = Header("")):
    auth(x_key)
    r = db.execute("SELECT data FROM snap WHERE user=?", (user,)).fetchone()
    return json.loads(r[0]) if r else {}


@app.put("/sync/{user}")
def put(user: str, body: dict, x_key: str = Header("")):
    auth(x_key)
    db.execute("INSERT OR REPLACE INTO snap VALUES(?,?)", (user, json.dumps(body)))
    db.commit()
    return {"ok": True}
