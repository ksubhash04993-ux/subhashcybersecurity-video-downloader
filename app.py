from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        filename = str(uuid.uuid4()) + ".mp4"
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        ydl_opts = {
            'outtmpl': filepath,
            'format': 'best'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(filepath, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
