from flask import Flask, request, send_file, send_from_directory
import yt_dlp
import io
import requests
import os
import shutil
import time

app = Flask(__name__)

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

src_cookie_path = os.path.join(root_dir, 'cookies.txt')


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

    # Vercel's filesystem is mostly read-only, so copy cookies to /tmp
    cookie_path = f'/tmp/cookies_{int(time.time() * 1000)}.txt'

    try:
        shutil.copy2(src_cookie_path, cookie_path)
    except Exception as e:
        return {"error": f"Could not load cookies: {str(e)}"}, 500

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,

        # Prefer a single MP4 file, then fall back to best available format
        'format': 'best[ext=mp4]/best',

        # Actually USE the cookies
        'cookiefile': cookie_path,

        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            video_url = info.get('url')
            title = info.get('title', 'video')

            if not video_url:
                return {"error": "Could not obtain video URL"}, 500

        response = requests.get(
            video_url,
            stream=True,
            timeout=60
        )

        response.raise_for_status()

        # Limit filename to something safer
        filename = ''.join(
            c for c in title
            if c.isalnum() or c in ' ._-'
        ).strip()

        if not filename:
            filename = 'video'

        return send_file(
            io.BytesIO(response.content),
            as_attachment=True,
            download_name=f'{filename}.mp4',
            mimetype='video/mp4'
        )

    except yt_dlp.utils.DownloadError as e:
        return {
            "error": "yt-dlp could not extract the video",
            "details": str(e)
        }, 400

    except requests.RequestException as e:
        return {
            "error": "Failed to retrieve video",
            "details": str(e)
        }, 502

    except Exception as e:
        return {
            "error": "Unexpected server error",
            "details": str(e)
        }, 500

    finally:
        try:
            os.remove(cookie_path)
        except OSError:
            pass


app = app


if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )