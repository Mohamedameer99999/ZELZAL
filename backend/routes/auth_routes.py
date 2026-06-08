from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from database import db
from models import User, Activity
from auth import create_user, authenticate_user, generate_tokens, is_valid_email, add_to_blocklist

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = getattr(request, '_parsed_data', request.get_json(silent=True) or {})
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required'}), 400

    if len(username) < 3 or len(username) > 30:
        return jsonify({'error': 'Username must be between 3 and 30 characters'}), 400

    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 400

    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    existing = db.session.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing:
        return jsonify({'error': 'Username or email already exists'}), 409

    user = create_user(username, email, password)
    db.session.add(user)
    db.session.commit()

    activity = Activity(user_id=user.id, action='Account created', category='auth')
    db.session.add(activity)
    db.session.commit()

    tokens = generate_tokens(user)
    return jsonify(tokens), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = getattr(request, '_parsed_data', request.get_json(silent=True) or {})
    username = data.get('username', '')
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = authenticate_user(db.session, username, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    activity = Activity(user_id=user.id, action='User logged in', category='auth')
    db.session.add(activity)
    db.session.commit()

    tokens = generate_tokens(user)
    return jsonify(tokens), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    add_to_blocklist(jti)
    return jsonify({'message': 'Successfully logged out'}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = db.session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user.to_dict()}), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    user = db.session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    tokens = generate_tokens(user)
    return jsonify({'access_token': tokens['access_token']}), 200
