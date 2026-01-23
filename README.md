# Soundboard
Simple soundboard app to play small sound effects.

## Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation & Running the App

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app using one of these methods:**

   **Option A: Direct Python execution**
   ```bash
   python app.py
   ```
   
   **Option B: Using Flask CLI (recommended)**
   ```bash
   flask run
   ```
   
   The app will be available at: `http://localhost:5000`

3. **Initialize the database (automatic on first run):**
   - The database will be automatically created on first startup
   - Or manually initialize with: `python -c "from app import app, db; app.app_context().push(); db.create_all()"`

4. **Create an account:**
   - Go to the home page and click **Register**
   - Create a username and password
   - Log in to access the soundboard

## Features
- Add sounds from YouTube links or upload audio files
- Play, pause, restart, and seek through sounds
- Delete sounds when no longer needed
- Local storage using IndexedDB for fast playback
- Easy YouTube authentication via Settings

## YouTube Downloads

### Easy Setup (Recommended)
1. Go to **Settings** (link in top-right corner)
2. Click **"Login to YouTube"**
3. A browser window will open automatically
4. Log into your YouTube account
5. Your credentials are saved automatically

You can now download:
- Age-restricted videos
- Region-locked content
- Videos with advanced protection

### Manual Setup (Alternative)
If you prefer not to use the built-in login:

1. Install a cookie export extension:
   - Chrome: [EditThisCookie](https://chromewebstore.google.com/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)
   - Firefox: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)
   
2. Visit youtube.com and log in
3. Export cookies using the extension
4. Save to: `~/.config/yt-dlp/cookies.txt`

### Still Having Issues?
- Try using **File Upload** instead of YouTube links
- Some public videos work without authentication
- Check that the YouTube video URL is correct and accessible
