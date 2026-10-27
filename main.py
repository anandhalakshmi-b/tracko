import os
from datetime import date, timedelta
 
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex as hx
 
from db import DB, iso
 
TX, MU, P, P2, OK, OR, RED, BG = "#171717", "#5f6368", "#2962ff", "#e91e63", "#00a86b", "#ff8f00", "#e53935", "#ffffff"
CATS = ["Technical", "Extra-curricular", "Fitness", "Language"]
 
 
def lbl(t, h=36, c=TX, **k):
    l = Label(text=t, color=hx(c), halign="left", valign="middle", size_hint_y=None, height=h, **k)
    l.bind(width=lambda w, v: setattr(w, "text_size", (v, None)))
    return l
 
 
def btn(t, cb, bg=P, **k):
    b = Button(text=t, background_normal="", background_color=hx(bg), color=(1, 1, 1, 1), **k)
    b.bind(on_release=lambda *_: cb())
    return b


def text_input(hint, **k):
    return TextInput(
        hint_text=hint, multiline=False, foreground_color=hx(TX),
        background_color=(1, 1, 1, 1), hint_text_color=hx(MU),
        cursor_color=hx(P), **k
    )


def page():
    sv = ScrollView()
    with sv.canvas.before:
        Color(*hx(BG))
        background = Rectangle(pos=sv.pos, size=sv.size)
    sv.bind(pos=lambda w, v: setattr(background, "pos", v),
            size=lambda w, v: setattr(background, "size", v))
    g = GridLayout(cols=1, spacing=8, padding=10, size_hint_y=None)
    g.bind(minimum_height=g.setter("height"))
    sv.add_widget(g)
    return sv, g
 
 
class Tracko(App):
    title = "Tracko"
    icon = "icon.png"
 
    def build(s):
        Window.clearcolor = hx(BG)
        s.db = DB(os.path.join(s.user_data_dir, "tracko.db"))
        s.day, s.cat, s.msg = iso(date.today()), CATS[0], ""
        root = BoxLayout(orientation="vertical")
        hdr = Label(text="Tracko", markup=True, bold=True, font_size=24,
                    color=hx(TX), size_hint_y=None, height=56)
        root.add_widget(hdr)
        tp = TabbedPanel(do_default_tab=False, tab_pos="bottom_mid", tab_height=48,
                         background_image="", background_color=hx(BG))
        s.pages = []
        for name, fn in [("Routine", s.t_routine), ("Streaks", s.t_streaks), ("To-Do", s.t_todo),
                         ("Skills", s.t_skills), ("Events", s.t_events)]:
            ti = TabbedPanelItem(text=name, background_normal="", background_down="",
                                 background_color=hx("#eaf0ff"), color=hx(TX))
            sv, g = page()
            ti.add_widget(sv)
            tp.add_widget(ti)
            s.pages.append((g, fn))
        root.add_widget(tp)
        s.refresh()
        s.hdr = hdr
        Clock.schedule_interval(s.tick, 30)
        return root
 
    # ---- plumbing ----
    def tick(s, *_):  # midnight rollover -> streaks re-evaluated
        if iso(date.today()) != s.day:
            s.day = iso(date.today())
            s.refresh()
 
    def refresh(s):
        for g, fn in s.pages:
            g.clear_widgets()
            fn(g)
 
    def ch(s):
        s.refresh()
 
    def say(s, m):
        s.msg = m
        s.refresh()
 
    def form(s, g, hints, fn, label="Add"):
        r = BoxLayout(size_hint_y=None, height=48, spacing=6)
        fs = []
        for h, w in hints:
            f = text_input(h, size_hint_x=w)
            fs.append(f)
            r.add_widget(f)
        r.add_widget(btn(label, lambda: fn(*[f.text.strip() for f in fs]), size_hint_x=.4))
        g.add_widget(r)
 
    # ---- tabs ----
    def t_routine(s, g):
        d, t = s.db.progress(s.day)
        g.add_widget(lbl(f"{s.day}   {d}/{t} done   Streak: {s.db.streak()}", h=44, bold=True))
        for r in s.db.applicable(s.day):
            row = BoxLayout(size_hint_y=None, height=48, spacing=6)
            cb = CheckBox(active=s.db.is_done(s.day, r["id"]), size_hint_x=None, width=48)
            cb.bind(active=lambda w, v, i=r["id"]: (s.db.set_done(s.day, i, v), s.ch()))
            row.add_widget(cb)
            row.add_widget(lbl(f'{r["time"]}  {r["title"]}', h=48))
            row.add_widget(btn("Del", lambda i=r["id"]: (s.db.end_routine(i), s.ch()), RED, size_hint_x=None, width=60))
            g.add_widget(row)
        s.form(g, [("New routine", .6), ("HH:MM", .3)],
               lambda t, tm: t and (s.db.add_routine(t, tm or "08:00"), s.ch()))
 
    def t_streaks(s, g):
        st = s.db.streak()
        g.add_widget(lbl(f"{st} day streak", h=70, bold=True, font_size=34, c=P2 if st == 0 else OK))
        n, t = s.db.progress(s.day)
        g.add_widget(lbl("Complete every routine today to keep it going." if n < t or t == 0
                         else "Today is complete. Keep it up!", h=40))
        g.add_widget(lbl("A missed day resets your streak to 0.", h=30, c=MU))
        row = BoxLayout(size_hint_y=None, height=70, spacing=4)
        for i in range(6, -1, -1):
            d = date.today() - timedelta(days=i)
            k = iso(d)
            if s.db.complete(k):
                sym, c = "OK", OK
            elif not s.db.applicable(k):
                sym, c = "-", MU
            elif i == 0:
                sym, c = "...", OR
            else:
                sym, c = "X", RED
            row.add_widget(Label(text=f"{d:%a}\n{sym}", color=hx(c), bold=True))
        g.add_widget(row)
 
    def t_todo(s, g):
        for t in s.db.q("SELECT * FROM todos ORDER BY x, id"):
            row = BoxLayout(size_hint_y=None, height=48, spacing=6)
            cb = CheckBox(active=bool(t["x"]), size_hint_x=None, width=48)
            cb.bind(active=lambda w, v, i=t["id"]: (s.db.x("UPDATE todos SET x=? WHERE id=?", (int(v), i)), s.ch()))
            row.add_widget(cb)
            row.add_widget(lbl(t["title"], h=48, c=MU if t["x"] else TX))
            row.add_widget(btn("Del", lambda i=t["id"]: (s.db.x("DELETE FROM todos WHERE id=?", (i,)), s.ch()), RED, size_hint_x=None, width=60))
            g.add_widget(row)
        s.form(g, [("New task", 1)], lambda t: t and (s.db.x("INSERT INTO todos(title) VALUES(?)", (t,)), s.ch()))
 
    def t_skills(s, g):
        r = BoxLayout(size_hint_y=None, height=48, spacing=6)
        sp = Spinner(text=s.cat, values=CATS, background_normal="", background_color=hx(P), color=(1, 1, 1, 1))
        sp.bind(text=lambda w, v: setattr(s, "cat", v))
        ti = text_input("Skill / hobby / language")
        r.add_widget(sp)
        r.add_widget(ti)
        r.add_widget(btn("Add", lambda: ti.text.strip() and (s.db.x("INSERT INTO skills(cat,name) VALUES(?,?)", (s.cat, ti.text.strip())), s.ch()), size_hint_x=.3))
        g.add_widget(r)
        for k in s.db.q("SELECT * FROM skills"):
            g.add_widget(lbl(f'{k["name"]}  [{k["cat"]}]   streak {s.db.skill_streak(k["id"])}', h=40, bold=True))
            log = s.db.q("SELECT note FROM skilllog WHERE sid=? AND day=?", (k["id"], s.day))
            if log:
                g.add_widget(lbl("Today: " + log[0]["note"], h=34, c=OK))
            else:
                s.form(g, [("What did you learn today?", 1)],
                       lambda n, i=k["id"]: n and (s.db.x("INSERT OR REPLACE INTO skilllog VALUES(?,?,?)", (i, s.day, n)), s.ch()), "Log")
            g.add_widget(btn("Delete skill", lambda i=k["id"]: (s.db.x("DELETE FROM skills WHERE id=?", (i,)), s.db.x("DELETE FROM skilllog WHERE sid=?", (i,)), s.ch()), RED, size_hint_y=None, height=34))
 
    def t_events(s, g):
        g.add_widget(lbl("Reminders show at 7, 3 and 1 day before.", h=30, c=MU))
        for e in s.db.q("SELECT * FROM events WHERE day>=? ORDER BY day", (s.day,)):
            n = (date.fromisoformat(e["day"]) - date.today()).days
            flag = "  << REMINDER" if n in (0, 1, 3, 7) else ""
            row = BoxLayout(size_hint_y=None, height=48, spacing=6)
            row.add_widget(lbl(f'{e["day"]}  {e["title"]}  (in {n}d){flag}', h=48, c=P2 if flag else TX))
            row.add_widget(btn("Del", lambda i=e["id"]: (s.db.x("DELETE FROM events WHERE id=?", (i,)), s.ch()), RED, size_hint_x=None, width=60))
            g.add_widget(row)
 
        def add(d, t):
            try:
                date.fromisoformat(d)
            except ValueError:
                return s.say("Use date format YYYY-MM-DD")
            if t:
                s.db.x("INSERT INTO events(day,title) VALUES(?,?)", (d, t))
                s.ch()
        s.form(g, [("YYYY-MM-DD", .4), ("Event", .5)], add)
 
if __name__ == "__main__":
    Tracko().run()