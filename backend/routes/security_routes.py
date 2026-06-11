from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database import db
from models import SecurityEvent
from datetime import datetime, timedelta, timezone

security_bp = Blueprint('security', __name__, url_prefix='/api/security')


@security_bp.route('/events', methods=['GET'])
@jwt_required()
def get_events():
    severity = request.args.get('severity')
    status = request.args.get('status')
    limit = request.args.get('limit', 50, type=int)

    query = db.session.query(SecurityEvent)
    if severity:
        query = query.filter(SecurityEvent.severity == severity)
    if status:
        query = query.filter(SecurityEvent.status == status)
    events = query.order_by(SecurityEvent.created_at.desc()).limit(limit).all()
    return jsonify({'events': [e.to_dict() for e in events]}), 200


@security_bp.route('/events', methods=['POST'])
@jwt_required()
def create_event():
    data = request.get_json() or {}
    event = SecurityEvent(
        event_type=data.get('event_type', 'unknown'),
        severity=data.get('severity', 'low'),
        source_ip=data.get('source_ip', ''),
        description=data.get('description', ''),
    )
    db.session.add(event)
    db.session.commit()
    return jsonify(event.to_dict()), 201


@security_bp.route('/events/<event_id>', methods=['PATCH'])
@jwt_required()
def update_event(event_id):
    event = db.session.query(SecurityEvent).get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    data = request.get_json() or {}
    if 'status' in data:
        event.status = data['status']
    db.session.commit()
    return jsonify(event.to_dict()), 200


@security_bp.route('/threat-map', methods=['GET'])
@jwt_required()
def get_threat_map():
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)

    threat_levels = {
        'critical': db.session.query(SecurityEvent).filter(
            SecurityEvent.severity == 'critical', SecurityEvent.created_at >= week_ago
        ).count(),
        'high': db.session.query(SecurityEvent).filter(
            SecurityEvent.severity == 'high', SecurityEvent.created_at >= week_ago
        ).count(),
        'medium': db.session.query(SecurityEvent).filter(
            SecurityEvent.severity == 'medium', SecurityEvent.created_at >= week_ago
        ).count(),
        'low': db.session.query(SecurityEvent).filter(
            SecurityEvent.severity == 'low', SecurityEvent.created_at >= week_ago
        ).count(),
    }

    events_by_type = {}
    events = db.session.query(SecurityEvent).filter(
        SecurityEvent.created_at >= week_ago
    ).all()
    for e in events:
        events_by_type[e.event_type] = events_by_type.get(e.event_type, 0) + 1

    return jsonify({
        'threat_levels': threat_levels,
        'events_by_type': events_by_type,
        'total_active_threats': sum(threat_levels.values()),
        'security_score': 85,
    }), 200


@security_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_reports():
    now = datetime.now(timezone.utc)
    month_ago = now - timedelta(days=30)

    total_events = db.session.query(SecurityEvent).filter(
        SecurityEvent.created_at >= month_ago
    ).count()

    resolved = db.session.query(SecurityEvent).filter(
        SecurityEvent.status == 'resolved', SecurityEvent.created_at >= month_ago
    ).count()

    return jsonify({
        'total_events': total_events,
        'resolved': resolved,
        'unresolved': total_events - resolved,
        'resolution_rate': round((resolved / total_events * 100) if total_events > 0 else 0, 1),
        'period': '30d',
    }), 200
