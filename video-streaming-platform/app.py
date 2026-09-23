import os, secrets, sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import *
from video_processor import get_video_metadata
from storage import Storage

BASE=os.path.dirname(os.path.abspath(__file__))
UPLOAD=os.path.join(BASE,"uploads")
ALLOWED={"mp4","webm","mov","mkv","avi","m4v"}
os.makedirs(UPLOAD,exist_ok=True)
app=Flask(__name__)
app.secret_key=os.getenv("SECRET_KEY","change-this-secret")
app.config["MAX_CONTENT_LENGTH"]=int(os.getenv("MAX_UPLOAD_MB","1024"))*1024*1024
init_db(); storage=Storage()

def allowed(name): return "." in name and name.rsplit(".",1)[1].lower() in ALLOWED
def user(): return get_user_by_id(session.get("user_id")) if session.get("user_id") else None
@app.context_processor
def inject(): return {"current_user":user()}
def login_required(f):
    @wraps(f)
    def w(*a,**k):
        if not session.get("user_id"):
            flash("Please log in first.","warning"); return redirect(url_for("login"))
        return f(*a,**k)
    return w

@app.route("/")
def index():
    q=request.args.get("q","").strip()
    return render_template("index.html",videos=list_videos(q),query=q)

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        u=request.form.get("username","").strip(); e=request.form.get("email","").strip().lower(); p=request.form.get("password","")
        if len(u)<3 or len(p)<6 or "@" not in e:
            flash("Use a valid username, email and password of at least 6 characters.","danger"); return render_template("register.html")
        try: create_user(u,e,generate_password_hash(p))
        except sqlite3.IntegrityError:
            flash("Username or email already exists.","danger"); return render_template("register.html")
        flash("Account created successfully.","success"); return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=get_user_by_username(request.form.get("username","").strip()); p=request.form.get("password","")
        if not u or not check_password_hash(u["password_hash"],p):
            flash("Invalid username or password.","danger"); return render_template("login.html")
        session.clear(); session["user_id"]=u["id"]; return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.get("/logout")
def logout(): session.clear(); flash("Logged out.","success"); return redirect(url_for("index"))

@app.get("/dashboard")
@login_required
def dashboard(): return render_template("dashboard.html",videos=get_user_videos(session["user_id"]))

@app.route("/upload",methods=["GET","POST"])
@login_required
def upload():
    if request.method=="POST":
        title=request.form.get("title","").strip(); desc=request.form.get("description","").strip(); f=request.files.get("video")
        if not title or not f or not f.filename or not allowed(f.filename):
            flash("Enter a title and choose a supported video file.","danger"); return render_template("upload.html")
        name=secure_filename(f.filename); unique=secrets.token_hex(8)+"_"+name; path=os.path.join(UPLOAD,unique); f.save(path)
        try:
            m=get_video_metadata(path); key=storage.save(path,unique)
            vid=create_video(session["user_id"],title,desc,name,key,os.path.getsize(path),m["duration"],m["mime_type"],m["width"],m["height"])
            if storage.uses_s3: os.remove(path)
            flash("Video uploaded successfully.","success"); return redirect(url_for("watch",video_id=vid))
        except Exception as ex:
            if os.path.exists(path): os.remove(path)
            flash("Upload failed: "+str(ex),"danger")
    return render_template("upload.html")

@app.get("/watch/<int:video_id>")
def watch(video_id):
    v=get_video(video_id)
    if not v: abort(404)
    increment_views(video_id); return render_template("watch.html",video=v)

@app.get("/stream/<int:video_id>")
def stream(video_id):
    v=get_video(video_id)
    if not v: abort(404)
    if storage.uses_s3: return redirect(storage.url(v["storage_key"]))
    name=os.path.basename(v["storage_key"]); path=os.path.join(UPLOAD,name)
    if not os.path.exists(path): abort(404)
    return send_from_directory(UPLOAD,name,mimetype=v["mime_type"],conditional=True)

@app.route("/edit/<int:video_id>",methods=["GET","POST"])
@login_required
def edit(video_id):
    v=get_video(video_id)
    if not v: abort(404)
    if v["user_id"]!=session["user_id"]: abort(403)
    if request.method=="POST":
        t=request.form.get("title","").strip()
        if not t: flash("Title is required.","danger")
        else:
            update_video(video_id,t,request.form.get("description","").strip()); flash("Video updated.","success"); return redirect(url_for("dashboard"))
    return render_template("edit.html",video=v)

@app.post("/delete/<int:video_id>")
@login_required
def delete(video_id):
    v=get_video(video_id)
    if not v: abort(404)
    if v["user_id"]!=session["user_id"]: abort(403)
    storage.delete(v["storage_key"]); delete_video(video_id); flash("Video deleted.","success"); return redirect(url_for("dashboard"))

@app.get("/api/videos")
def api_videos(): return jsonify([dict(v) for v in list_videos(request.args.get("q","").strip())])

@app.errorhandler(413)
def too_large(e): flash("File exceeds upload limit.","danger"); return redirect(url_for("upload"))

if __name__=="__main__": app.run(host="127.0.0.1",port=int(os.getenv("PORT","5000")),debug=True)
