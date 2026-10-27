import sqlite3
from datetime import date, timedelta

def iso(d):
    return d.isoformat()


class DB:
    def __init__(s, path):
        s.c = sqlite3.connect(path)
        s.c.row_factory = sqlite3.Row
        s.c.executescript("""
        CREATE TABLE IF NOT EXISTS routines(id INTEGER PRIMARY KEY, title TEXT, time TEXT, created TEXT, ended TEXT);
        CREATE TABLE IF NOT EXISTS done(day TEXT, rid INTEGER, PRIMARY KEY(day, rid));
        CREATE TABLE IF NOT EXISTS todos(id INTEGER PRIMARY KEY, title TEXT, x INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, day TEXT, title TEXT);
        CREATE TABLE IF NOT EXISTS skills(id INTEGER PRIMARY KEY, cat TEXT, name TEXT);
        CREATE TABLE IF NOT EXISTS skilllog(sid INTEGER, day TEXT, note TEXT, PRIMARY KEY(sid, day));
        """)

    def q(s, sql, a=()):
        return s.c.execute(sql, a).fetchall()

    def x(s, sql, a=()):
        s.c.execute(sql, a)
        s.c.commit()

    # ---- routines ----
    def add_routine(s, title, tm):
        s.x("INSERT INTO routines(title,time,created) VALUES(?,?,?)", (title, tm, iso(date.today())))

    def end_routine(s, rid):
        s.x("UPDATE routines SET ended=? WHERE id=?", (iso(date.today()), rid))

    def applicable(s, day):
        return s.q("SELECT * FROM routines WHERE created<=? AND (ended IS NULL OR ended>?) ORDER BY time", (day, day))

    def is_done(s, day, rid):
        return bool(s.q("SELECT 1 FROM done WHERE day=? AND rid=?", (day, rid)))

    def set_done(s, day, rid, v):
        if v:
            s.x("INSERT OR IGNORE INTO done VALUES(?,?)", (day, rid))
        else:
            s.x("DELETE FROM done WHERE day=? AND rid=?", (day, rid))

    def progress(s, day):
        ids = [r["id"] for r in s.applicable(day)]
        n = sum(1 for i in ids if s.is_done(day, i))
        return n, len(ids)

    def complete(s, day):
        n, t = s.progress(day)
        return t > 0 and n == t

    # ---- streaks (computed from history, so a missed day resets it to 0 automatically) ----
    def streak(s):
        d = date.today()
        if not s.complete(iso(d)):
            d -= timedelta(days=1)  # today still in progress; judge from yesterday
        n = 0
        while n < 3650 and s.complete(iso(d)):
            n += 1
            d -= timedelta(days=1)
        return n

    def skill_streak(s, sid):
        d = date.today()
        if not s.q("SELECT 1 FROM skilllog WHERE sid=? AND day=?", (sid, iso(d))):
            d -= timedelta(days=1)
        n = 0
        while n < 3650 and s.q("SELECT 1 FROM skilllog WHERE sid=? AND day=?", (sid, iso(d))):
            n += 1
            d -= timedelta(days=1)
        return n
