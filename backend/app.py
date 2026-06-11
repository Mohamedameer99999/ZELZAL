from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from database import init_db, create_tables
from config import Config
from auth import sanitize_input, is_jti_blocklisted

import os

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
app.config.from_object(Config)

CORS(app, resources={r"/api/*": {"origins": "*"}})
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return is_jti_blocklisted(jti)


limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[Config.RATELIMIT_DEFAULT],
    storage_uri=Config.RATELIMIT_STORAGE_URL,
    enabled=Config.RATELIMIT_ENABLED,
)

init_db(app)

from models import User, Activity, SecurityEvent, Project, Task, Conversation, AnalyticsEvent  # noqa: E402, F401

create_tables(app)

from routes.auth_routes import auth_bp  # noqa: E402
from routes.dashboard_routes import dashboard_bp  # noqa: E402
from routes.security_routes import security_bp  # noqa: E402
from routes.ai_routes import ai_bp  # noqa: E402
from routes.projects_routes import projects_bp  # noqa: E402
from routes.analytics_routes import analytics_bp  # noqa: E402
from routes.users_routes import users_bp  # noqa: E402

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(security_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(users_bp)


@app.after_request
def add_security_headers(resp):
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'DENY'
    resp.headers['X-XSS-Protection'] = '1; mode=block'
    resp.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    resp.headers['Content-Security-Policy'] = (
        "default-src 'self'; script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "connect-src 'self' ws: wss:; img-src 'self' data:;"
    )
    resp.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    resp.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return resp


@app.before_request
def validate_input():
    if request.method in ('POST', 'PUT', 'PATCH'):
        if request.is_json:
            data = request.get_json(silent=True) or {}
            sanitized = {}
            for k, v in data.items():
                if isinstance(v, str):
                    sanitized[k] = sanitize_input(v)
                else:
                    sanitized[k] = v
            request._parsed_data = sanitized


@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')


@app.errorhandler(404)
def not_found(e):
    return {'error': 'Not found'}, 404


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded. Try again later.'}), 429


@app.errorhandler(500)
def server_error(e):
    return {'error': 'Internal server error'}, 500


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('ai_message')
def handle_ai_message(data):
    message = data.get('message', '')
    socketio.emit('ai_response', {'response': f'Echo: {message}'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    socketio.run(app, debug=debug, host='0.0.0.0', port=port)
