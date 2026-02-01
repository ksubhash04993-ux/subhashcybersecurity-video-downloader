from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import uuid
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = False  # Production mode

# Rate limiting: 5 downloads per minute per IP
limiter = Limiter(app, key_func=get_remote_address)

DOWNLOAD_DIR = "/tmp"  # Render-safe temp directory

@app.route("/")
def home():
    return "SubhashCyberSecurity Backend Running"

@app.route("/download", methods=["POST"])
@limiter.limit("5/minute")
def download():
    try:
        data = request.get_json()
        url = data.get("url")
        quality = data.get("quality", "best")
        mp3 = data.get("mp3", False)

        if not url:
            return jsonify({"error": "URL missing"}), 400

        # Generate safe filename
        ext = "mp3" if mp3 else "mp4"
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        # yt-dlp options
        ydl_opts = {"outtmpl": filepath}
        if mp3:
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            if quality != "best":
                ydl_opts["format"] = f"bestvideo[height<={quality}]+bestaudio/best"
            else:
                ydl_opts["format"] = "best"

        # Download video/audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
