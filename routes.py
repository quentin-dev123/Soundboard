from app import app, db, SOUNDS_DIR
from models import Account, Sound
from flask import request, jsonify, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import download_yt_audio, authenticate_youtube, is_youtube_authenticated
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
    youtube_authenticated = is_youtube_authenticated()
    return render_template('settings.html', youtube_authenticated=youtube_authenticated)

@app.route('/api/youtube-status', methods=['GET'])
@login_required
def youtube_status():
    """Check YouTube authentication status."""
    return jsonify({
        'authenticated': is_youtube_authenticated(),
        'message': 'YouTube authenticated' if is_youtube_authenticated() else 'YouTube not authenticated'
    })

@app.route('/api/youtube-login', methods=['POST'])
@login_required
def youtube_login():
    """Start YouTube authentication process."""
    try:
        # Run async authentication in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(authenticate_youtube())
        loop.close()
        
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Authentication failed: {str(e)}'
        }), 500

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
    
    if data.get('yt_url'):
        try:
            rel_path = download_yt_audio(data['yt_url'], user_id)
            
            sound = Sound(user_id=user_id, title=title, file_path=rel_path)
            db.session.add(sound)
            db.session.commit()
            
            # Read file and return COMPLETE sound
            full_path = SOUNDS_DIR / rel_path
            with open(full_path, 'rb') as f:
                audio_data = f.read()
            
            return jsonify({
                'id': sound.id,
                'title': sound.title,
                'file_path': sound.file_path,
                'audio_base64': base64.b64encode(audio_data).decode('utf-8')
            }), 201
        except Exception as e:
            error_msg = str(e)
            # Provide helpful error messages for common YouTube issues
            if 'Sign in to confirm' in error_msg or 'bot' in error_msg.lower():
                return jsonify({
                    'error': 'YouTube requires authentication. Please try a different video or use file upload instead. Some videos are protected from downloads.'
                }), 400
            elif 'video not found' in error_msg.lower() or 'not available' in error_msg.lower():
                return jsonify({
                    'error': 'Video not found or not available. Check the URL or try a different video.'
                }), 400
            else:
                return jsonify({'error': f'YouTube download failed: {error_msg}'}), 400
    
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
            
            return jsonify({
                'id': sound.id,
                'title': sound.title,
                'file_path': sound.file_path,
                'audio_base64': audio_base64
            }), 201
        except Exception as e:
            return jsonify({'error': f'File upload failed: {str(e)}'}), 400
    
    return jsonify({'error': 'Either yt_url or audio_base64 required'}), 400


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