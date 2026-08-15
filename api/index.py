from flask import Flask, request, send_file, send_from_directory
import yt_dlp
import io
import requests
import os
import shutil
import time

app = Flask(__name__)

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths to your cookie file
src_cookie_path = os.path.join(root_dir, 'cookies.txt')
tmp_cookie_path = '/tmp/cookies.txt'

@app.route('/')
def index():
    return send_from_directory(root_dir, 'index.html')

@app.route('/downloader')
def downloader():
    return send_from_directory(root_dir, 'downloader.html')

@app.route('/api/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    if not url:
        return {"error": "Missing url parameter"}, 400

    # Copy cookie file to writable /tmp directory
    try:
        # Use a unique filename to avoid race conditions
        unique_cookie_path = f'/tmp/cookies_{int(time.time())}.txt'
        shutil.copy2(src_cookie_path, unique_cookie_path)
        cookie_path = unique_cookie_path
    except Exception as e:
        print(f"Could not copy cookies: {e}")
        # Fallback: try the original path if copying fails
        cookie_path = src_cookie_path

    ydl_opts = {
        'quiet': True,
        'format': 'bestvideo+bestaudio/best',
        'cookiefile': cookie_path,
        'no_cookies': True,
        'nooverwrites': True,
    }

    try:
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
    finally:
        # Clean up the temporary cookie file
        if cookie_path != src_cookie_path:
            try:
                os.remove(cookie_path)
            except:
                pass

# Vercel needs this
app = app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)