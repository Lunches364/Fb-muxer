import base64, glob, hashlib, os, subprocess, time, requests
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse

app = FastAPI()
HEADERS = {"User-Agent": "Mozilla/5.0"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.api_route("/mux.mp4", methods=["GET", "HEAD"])
def mux_video(v: str = Query(None), a: str = Query(None), vb64: str = Query(None), ab64: str = Query(None)):
    for f in glob.glob("/tmp/*.mp4"):
        if time.time() - os.path.getmtime(f) > 600:
            try: os.remove(f)
            except: pass

    if vb64 and ab64:
        v = base64.urlsafe_b64decode(vb64 + "===").decode()
        a = base64.urlsafe_b64decode(ab64 + "===").decode()

    uid = hashlib.md5((v + a).encode()).hexdigest()
    out_path = f"/tmp/{uid}.mp4"

    if not os.path.exists(out_path):
        v_path, a_path = f"/tmp/{uid}_v.mp4", f"/tmp/{uid}_a.m4a"
        with open(v_path, "wb") as fv:
            fv.write(requests.get(v, headers=HEADERS, timeout=45).content)
        with open(a_path, "wb") as fa:
            fa.write(requests.get(a, headers=HEADERS, timeout=45).content)

        cmd = ["ffmpeg", "-y", "-i", v_path, "-i", a_path, "-c", "copy", "-movflags", "+faststart", out_path]
        subprocess.run(cmd, check=True)
        os.remove(v_path)
        os.remove(a_path)

    return FileResponse(out_path, media_type="video/mp4", filename="video.mp4")
