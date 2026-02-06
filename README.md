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
- Upload audio files (MP3, WAV, FLAC, etc.)
- Play, pause, restart, and seek through sounds
- Delete sounds when no longer needed
- Drag to reorder sounds and organize your soundboard
- Local storage using IndexedDB for fast playback
- Background upload with automatic sync to server
