from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import User, Activity, SecurityEvent, Project, Task, AnalyticsEvent
from datetime import datetime, timedelta, timezone

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    user_id = get_jwt_identity()
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total_users = db.session.query(User).count()
    active_users = db.session.query(User).filter(User.is_active == True).count()
    total_projects = db.session.query(Project).count()
    active_projects = db.session.query(Project).filter(Project.status == 'active').count()
    total_tasks = db.session.query(Task).count()
    completed_tasks = db.session.query(Task).filter(Task.status == 'done').count()
    security_events = db.session.query(SecurityEvent).filter(SecurityEvent.status == 'active').count()
    critical_events = db.session.query(SecurityEvent).filter(
        SecurityEvent.severity == 'critical', SecurityEvent.status == 'active'
    ).count()

    today_activities = db.session.query(Activity).filter(
        Activity.created_at >= today_start
    ).count()

    return jsonify({
        'total_users': total_users,
        'active_users': active_users,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'security_events': security_events,
        'critical_events': critical_events,
        'today_activities': today_activities,
        'task_completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
    }), 200


@dashboard_bp.route('/activities', methods=['GET'])
@jwt_required()
def get_activities():
    limit = request.args.get('limit', 20, type=int)
    activities = db.session.query(Activity).order_by(
        Activity.created_at.desc()
    ).limit(limit).all()
    return jsonify({'activities': [a.to_dict() for a in activities]}), 200


@dashboard_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_overview():
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    recent_events = db.session.query(SecurityEvent).filter(
        SecurityEvent.created_at >= week_ago
    ).order_by(SecurityEvent.created_at.desc()).limit(5).all()

    recent_projects = db.session.query(Project).order_by(
        Project.created_at.desc()
    ).limit(5).all()

    return jsonify({
        'recent_events': [e.to_dict() for e in recent_events],
        'recent_projects': [p.to_dict() for p in recent_projects],
        'system_health': 98.5,
        'uptime': '99.9%',
        'server_status': 'operational',
    }), 200
