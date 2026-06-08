from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Conversation, Activity
from datetime import datetime, timezone

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

AI_RESPONSES = {
    'security': 'I recommend enabling multi-factor authentication and reviewing your active sessions regularly. Would you like me to run a security audit?',
    'performance': 'Your system performance is optimal. I suggest clearing cache and running a disk cleanup to maintain efficiency.',
    'threat': 'I detected unusual patterns in your network traffic. Consider isolating affected systems and running a full vulnerability scan.',
    'project': 'Based on your project timeline, I recommend prioritizing critical tasks with approaching deadlines. Shall I generate a sprint report?',
    'analytics': 'User engagement has increased by 23% this week. Your security protocols are effectively maintaining trust.',
    'default': 'I am monitoring your systems continuously. All security parameters are within normal ranges. How can I assist with your cybersecurity operations?',
}


@ai_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    conversation_id = data.get('conversation_id')

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    conversation = None
    if conversation_id:
        conversation = db.session.query(Conversation).filter(
            Conversation.id == conversation_id, Conversation.user_id == user_id
        ).first()

    if not conversation:
        conversation = Conversation(user_id=user_id, title=message[:50])
        db.session.add(conversation)
        db.session.flush()

    if conversation.messages is None:
        conversation.messages = []

    msg_lower = message.lower()
    if any(w in msg_lower for w in ['security', 'auth', 'login', 'password', 'mfa', '2fa']):
        response = AI_RESPONSES['security']
    elif any(w in msg_lower for w in ['performance', 'speed', 'slow', 'fast', 'optimize']):
        response = AI_RESPONSES['performance']
    elif any(w in msg_lower for w in ['threat', 'attack', 'virus', 'malware', 'breach', 'hack']):
        response = AI_RESPONSES['threat']
    elif any(w in msg_lower for w in ['project', 'task', 'sprint', 'deadline']):
        response = AI_RESPONSES['project']
    elif any(w in msg_lower for w in ['analytics', 'report', 'metric', 'stat']):
        response = AI_RESPONSES['analytics']
    else:
        response = AI_RESPONSES['default']

    conversation.messages.append({'role': 'user', 'content': message, 'timestamp': datetime.now(timezone.utc).isoformat()})
    conversation.messages.append({'role': 'assistant', 'content': response, 'timestamp': datetime.now(timezone.utc).isoformat()})
    conversation.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({
        'response': response,
        'conversation_id': conversation.id,
        'conversation': conversation.to_dict(),
    }), 200


@ai_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    user_id = get_jwt_identity()
    conversations = db.session.query(Conversation).filter(
        Conversation.user_id == user_id
    ).order_by(Conversation.updated_at.desc()).limit(20).all()
    return jsonify({'conversations': [c.to_dict() for c in conversations]}), 200


@ai_bp.route('/conversations/<conversation_id>', methods=['GET'])
@jwt_required()
def get_conversation(conversation_id):
    user_id = get_jwt_identity()
    conversation = db.session.query(Conversation).filter(
        Conversation.id == conversation_id, Conversation.user_id == user_id
    ).first()
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    return jsonify({'conversation': conversation.to_dict()}), 200


@ai_bp.route('/conversations/<conversation_id>', methods=['DELETE'])
@jwt_required()
def delete_conversation(conversation_id):
    user_id = get_jwt_identity()
    conversation = db.session.query(Conversation).filter(
        Conversation.id == conversation_id, Conversation.user_id == user_id
    ).first()
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    db.session.delete(conversation)
    db.session.commit()
    return jsonify({'message': 'Conversation deleted'}), 200


@ai_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    recommendations = [
        {'type': 'security', 'title': 'Enable 2FA', 'description': 'Strengthen your account security with two-factor authentication', 'priority': 'high'},
        {'type': 'performance', 'title': 'System Optimization', 'description': 'Run a full system diagnostic to identify potential bottlenecks', 'priority': 'medium'},
        {'type': 'project', 'title': 'Review Project Timeline', 'description': '3 projects are approaching their deadlines', 'priority': 'high'},
        {'type': 'analytics', 'title': 'Weekly Report Ready', 'description': 'Your weekly security analytics report is available for review', 'priority': 'low'},
    ]
    return jsonify({'recommendations': recommendations}), 200
