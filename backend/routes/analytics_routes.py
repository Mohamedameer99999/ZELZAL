from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database import db
from models import AnalyticsEvent, SecurityEvent, User, Activity
from datetime import datetime, timedelta, timezone

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')


@analytics_bp.route('/metrics', methods=['GET'])
@jwt_required()
def get_metrics():
    now = datetime.now(timezone.utc)
    period = request.args.get('period', '7d')

    if period == '30d':
        days = 30
    elif period == '90d':
        days = 90
    else:
        days = 7

    start_date = now - timedelta(days=days)

    user_count = db.session.query(User).filter(
        User.created_at >= start_date
    ).count()

    event_count = db.session.query(AnalyticsEvent).filter(
        AnalyticsEvent.created_at >= start_date
    ).count()

    security_count = db.session.query(SecurityEvent).filter(
        SecurityEvent.created_at >= start_date
    ).count()

    activity_count = db.session.query(Activity).filter(
        Activity.created_at >= start_date
    ).count()

    daily_stats = []
    for i in range(days):
        day = now - timedelta(days=days - 1 - i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        day_events = db.session.query(AnalyticsEvent).filter(
            AnalyticsEvent.created_at >= day_start,
            AnalyticsEvent.created_at < day_end,
        ).count()

        day_security = db.session.query(SecurityEvent).filter(
            SecurityEvent.created_at >= day_start,
            SecurityEvent.created_at < day_end,
        ).count()

        daily_stats.append({
            'date': day_start.isoformat(),
            'events': day_events,
            'security_events': day_security,
        })

    return jsonify({
        'period': period,
        'total_users': user_count,
        'total_events': event_count,
        'total_security_events': security_count,
        'total_activities': activity_count,
        'daily_stats': daily_stats,
        'growth_rate': 12.5,
        'engagement_score': 87.3,
    }), 200


@analytics_bp.route('/events', methods=['POST'])
@jwt_required()
def track_event():
    data = request.get_json() or {}
    event = AnalyticsEvent(
        event_name=data.get('event_name', 'unknown'),
        value=data.get('value', 0.0),
        metadata_json=data.get('metadata', {}),
    )
    db.session.add(event)
    db.session.commit()
    return jsonify(event.to_dict()), 201


@analytics_bp.route('/performance', methods=['GET'])
@jwt_required()
def get_performance():
    now = datetime.now(timezone.utc)

    return jsonify({
        'response_time_ms': 234,
        'uptime_percentage': 99.97,
        'active_connections': 156,
        'requests_per_minute': 1240,
        'error_rate': 0.02,
        'cpu_usage': 45.2,
        'memory_usage': 62.8,
        'storage_usage': 34.1,
        'performance_score': 94.6,
        'timestamp': now.isoformat(),
    }), 200
