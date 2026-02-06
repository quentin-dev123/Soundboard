from app import app, db, SOUNDS_DIR
from models import Account, Sound
from flask import request, jsonify, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
# YouTube-specific helpers removed; helpers.py now contains only general helpers (if any)
import base64
import time
import asyncio

@app.cli.command()
def db_init():
    """Create tables."""
    db.create_all()
    print("Tables created.")

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/register')
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('soundboard'))
    return render_template('register.html')

@app.route('/login')
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('soundboard'))
    return render_template('login.html')

@app.route('/soundboard')
@login_required
def soundboard():
    return render_template('soundboard.html')

@app.route('/settings')
@login_required
def settings():
    # YouTube authentication support removed — render settings page without YouTube options
    return render_template('settings.html')

# YouTube API endpoints removed

# YouTube authentication endpoint removed

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    if Account.query.filter_by(username=username).first():
        return jsonify({'error': 'Username exists'}), 400
    account = Account(username=username, password_hash=generate_password_hash(password))
    db.session.add(account)
    db.session.commit()
    return jsonify({'message': 'Registered'}), 201

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    account = Account.query.filter_by(username=data['username']).first()
    if account and check_password_hash(account.password_hash, data['password']):
        login_user(account)
        return jsonify({'message': 'Logged in'}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out'}), 200


@app.route('/api/sounds', methods=['GET'])
@login_required
def get_all_sounds():
    user_id = current_user.id
    sounds = Sound.query.filter_by(user_id=user_id).all()
    
    result = []
    for sound in sounds:
        full_path = SOUNDS_DIR / sound.file_path
        if full_path.exists():
            with open(full_path, 'rb') as f:
                audio_data = f.read()
            result.append({
                'id': sound.id,
                'title': sound.title,
                'file_path': sound.file_path,
                'audio_base64': base64.b64encode(audio_data).decode('utf-8')
            })
    
    return jsonify(result), 200

@app.route('/new_sound', methods=['POST'])
@login_required
def new_sound():
    try:
        data = request.get_json(force=True)
    except Exception as e:
        return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    user_id = current_user.id
    title = data.get('title', 'Untitled')
    
    # YouTube URL uploads are not supported anymore
    if data.get('yt_url'):
        return jsonify({'error': 'YouTube URL uploads are not supported. Please upload a file instead.'}), 400
    
    elif data.get('audio_base64'):
        try:
            audio_base64 = data['audio_base64']
            # Decode base64 to binary
            audio_bytes = base64.b64decode(audio_base64)
            
            timestamp = int(time.time() * 1000)
            file_name = f"{timestamp}.mp3"
            rel_path = f"user_{user_id}/{file_name}"
            full_path = SOUNDS_DIR / rel_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'wb') as f:
                f.write(audio_bytes)
            
            sound = Sound(user_id=user_id, title=title, file_path=rel_path)
            db.session.add(sound)
            db.session.commit()
            
            # Return lightweight success response — do not send audio back to client here
            return jsonify({
                'id': sound.id,
                'title': sound.title,
                'file_path': sound.file_path,
                'message': 'Sound saved'
            }), 201
        except Exception as e:
            return jsonify({'error': f'File upload failed: {str(e)}'}), 400
    
    return jsonify({'error': 'Either yt_url or audio_base64 required'}), 400


@app.route('/api/sound/<int:sound_id>', methods=['GET'])
@login_required
def get_sound(sound_id):
    """Return a single sound's metadata and base64 audio data."""
    user_id = current_user.id
    sound = Sound.query.filter_by(id=sound_id, user_id=user_id).first()
    if not sound:
        return jsonify({'error': 'Sound not found'}), 404

    full_path = SOUNDS_DIR / sound.file_path
    if not full_path.exists():
        return jsonify({'error': 'Audio file missing on server'}), 404

    with open(full_path, 'rb') as f:
        audio_data = f.read()

    return jsonify({
        'id': sound.id,
        'title': sound.title,
        'file_path': sound.file_path,
        'audio_base64': base64.b64encode(audio_data).decode('utf-8')
    }), 200


@app.route('/delete_sound/<int:sound_id>', methods=['DELETE'])
@login_required
def delete_sound(sound_id):
    user_id = current_user.id
    
    # Find sound and verify ownership
    sound = Sound.query.filter_by(id=sound_id, user_id=user_id).first()
    if not sound:
        return jsonify({'error': 'Sound not found'}), 404
    
    # Delete file from disk
    full_path = SOUNDS_DIR / sound.file_path
    if full_path.exists():
        full_path.unlink()
    
    # Delete from database
    db.session.delete(sound)
    db.session.commit()
    
    return jsonify({'message': 'Sound deleted'}), 200