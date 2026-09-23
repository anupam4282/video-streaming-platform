import subprocess,json,mimetypes
def get_video_metadata(path):
    r={"duration":0,"width":0,"height":0,"mime_type":mimetypes.guess_type(path)[0] or "video/mp4"}
    try:
        x=subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height:format=duration","-of","json",path],capture_output=True,text=True,check=True)
        d=json.loads(x.stdout); s=(d.get("streams") or [{}])[0]; f=d.get("format") or {}
        r["width"]=int(s.get("width") or 0); r["height"]=int(s.get("height") or 0); r["duration"]=float(f.get("duration") or 0)
    except Exception: pass
    return r
