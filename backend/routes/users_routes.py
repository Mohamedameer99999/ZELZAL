from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import User, Activity
from auth import hash_password

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


@users_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    current_id = get_jwt_identity()
    current = db.session.query(User).get(current_id)
    if not current or current.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    users = db.session.query(User).order_by(User.created_at.desc()).all()
    return jsonify({'users': [u.to_dict() for u in users]}), 200


@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = db.session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user.to_dict()}), 200


@users_bp.route('/profile', methods=['PATCH'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = db.session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json() or {}
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'bio' in data:
        user.bio = data['bio']
    if 'avatar' in data:
        user.avatar = data['avatar']
    if 'password' in data and data['password']:
        user.password_hash = hash_password(data['password'])

    db.session.commit()

    activity = Activity(user_id=user_id, action='Profile updated', category='user')
    db.session.add(activity)
    db.session.commit()

    return jsonify({'user': user.to_dict()}), 200


@users_bp.route('/<user_id>/role', methods=['PATCH'])
@jwt_required()
def update_role(user_id):
    current_id = get_jwt_identity()
    current = db.session.query(User).get(current_id)
    if not current or current.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    user = db.session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json() or {}
    if 'role' in data:
        user.role = data['role']
    db.session.commit()
    return jsonify({'user': user.to_dict()}), 200


@users_bp.route('/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_id = get_jwt_identity()
    current = db.session.query(User).get(current_id)
    if not current or current.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    user = db.session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if user.id == current_id:
        return jsonify({'error': 'Cannot delete yourself'}), 400

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200
