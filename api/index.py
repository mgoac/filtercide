from flask import Flask, request, send_file, send_from_directory
import yt_dlp
import io
import requests
import os

app = Flask(__name__)


@app.route('/')
def index():
    return send_from_directory(root_dir, 'index.html')

@app.route('/downloader')
def downloader():
    return send_from_directory(root_dir, 'downloader.html')

#e
@app.route('/api/download', methods=['GET'])
def download_video():
    
    url = request.args.get('url')
    if not url:
        return {"error": "Missing url parameter"}, 400


    ydl_opts = {'quiet': True, 'format': 'best[ext=mp4]'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        video_url = info['url']
        title = info.get('title', 'video')


    response = requests.get(video_url, stream=True)


    return send_file(
        io.BytesIO(response.content),
        as_attachment=True,
        download_name=f"{title}.mp4",
        mimetype='video/mp4'
    )

# Vercel needs this
app = app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)