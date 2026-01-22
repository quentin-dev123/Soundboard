from app import app, db, jwt, SOUNDS_DIR
from models import Account, Sound
from flask import request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from helpers import download_yt_audio
import base64

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

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
def login():
    data = request.get_json()
    account = Account.query.filter_by(username=data['username']).first()
    if account and check_password_hash(account.password_hash, data['password']):
        token = create_access_token(identity=account.id)
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/new_sound', methods=['POST'])
@jwt_required()
def new_sound():
    data = request.get_json()
    user_id = get_jwt_identity()
    
    if data.get('yt_url'):
        title = data.get('title', 'Untitled')
        rel_path = download_yt_audio(data['yt_url'], user_id)  # Your existing function
        
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
            'audio_base64': base64.b64encode(audio_data).decode('utf-8')  # Full MP3 as base64
        }), 201

@app.route('/sounds/<int:sound_id>', methods=['GET'])  # Individual sound fetch
@jwt_required()
def get_sound(sound_id):
    user_id = get_jwt_identity()
    sound = Sound.query.filter_by(id=sound_id, user_id=user_id).first_or_404()
    
    full_path = SOUNDS_DIR / sound.file_path
    with open(full_path, 'rb') as f:
        audio_data = f.read()
    
    return jsonify({
        'id': sound.id,
        'title': sound.title,
        'file_path': sound.file_path,
        'audio_base64': base64.b64encode(audio_data).decode('utf-8')
    })

@app.route('/delete_sound/<int:sound_id>', methods=['DELETE'])
@jwt_required()
def delete_sound(sound_id):
    user_id = get_jwt_identity()
    
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




if __name__ == '__main__':
    app.run(debug=True)