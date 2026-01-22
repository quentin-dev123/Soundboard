from app import app, db, SOUNDS_DIR
from uuid import uuid4
from yt_dlp import YoutubeDL

@app.cli.command()
def db_init():
    """Create tables."""
    db.create_all()
    print("Tables created.")

def download_yt_audio(url, user_id):
    """Download YouTube audio as mp3."""
    user_dir = SOUNDS_DIR / str(user_id)
    user_dir.mkdir(exist_ok=True)
    filename = f"{uuid4()}.mp3"
    filepath = user_dir / filename

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(filepath.with_suffix('.%(ext)s')),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return str(filepath.relative_to(SOUNDS_DIR))