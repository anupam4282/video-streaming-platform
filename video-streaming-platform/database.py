import os, sqlite3
from datetime import datetime, timezone
BASE=os.path.dirname(os.path.abspath(__file__)); DB=os.path.join(BASE,"data","videos.db")
def db():
    os.makedirs(os.path.dirname(DB),exist_ok=True); c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init_db():
    with db() as c:
        c.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE,email TEXT UNIQUE,password_hash TEXT,created_at TEXT)")
        c.execute("""CREATE TABLE IF NOT EXISTS videos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,title TEXT,description TEXT,filename TEXT,storage_key TEXT,
        size_bytes INTEGER,duration REAL,mime_type TEXT,width INTEGER,height INTEGER,views INTEGER DEFAULT 0,created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id))"""); c.commit()
def create_user(u,e,p):
    with db() as c:
        x=c.execute("INSERT INTO users(username,email,password_hash,created_at) VALUES(?,?,?,?)",(u,e,p,datetime.now(timezone.utc).isoformat())); c.commit(); return x.lastrowid
def get_user_by_username(u):
    with db() as c:return c.execute("SELECT * FROM users WHERE username=?",(u,)).fetchone()
def get_user_by_id(i):
    if not i:return None
    with db() as c:return c.execute("SELECT * FROM users WHERE id=?",(i,)).fetchone()
def create_video(uid,t,d,f,k,s,dur,mime,w,h):
    with db() as c:
        x=c.execute("INSERT INTO videos(user_id,title,description,filename,storage_key,size_bytes,duration,mime_type,width,height,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",(uid,t,d,f,k,s,dur,mime,w,h,datetime.now(timezone.utc).isoformat())); c.commit(); return x.lastrowid
def get_video(i):
    with db() as c:return c.execute("SELECT videos.*,users.username FROM videos JOIN users ON users.id=videos.user_id WHERE videos.id=?",(i,)).fetchone()
def list_videos(q=""):
    with db() as c:
        if q:
            x="%"+q+"%"; return c.execute("SELECT videos.*,users.username FROM videos JOIN users ON users.id=videos.user_id WHERE videos.title LIKE ? OR videos.description LIKE ? ORDER BY videos.id DESC",(x,x)).fetchall()
        return c.execute("SELECT videos.*,users.username FROM videos JOIN users ON users.id=videos.user_id ORDER BY videos.id DESC").fetchall()
def get_user_videos(uid):
    with db() as c:return c.execute("SELECT * FROM videos WHERE user_id=? ORDER BY id DESC",(uid,)).fetchall()
def update_video(i,t,d):
    with db() as c:c.execute("UPDATE videos SET title=?,description=? WHERE id=?",(t,d,i)); c.commit()
def delete_video(i):
    with db() as c:c.execute("DELETE FROM videos WHERE id=?",(i,)); c.commit()
def increment_views(i):
    with db() as c:c.execute("UPDATE videos SET views=views+1 WHERE id=?",(i,)); c.commit()
