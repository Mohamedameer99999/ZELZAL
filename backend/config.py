import os
from datetime import timedelta

def _required_env(key: str, fallback: str = None) -> str:
    val = os.environ.get(key)
    if not val:
        if fallback:
            return fallback
        raise RuntimeError(f'{key} environment variable is required')
    return val

class Config:
    SECRET_KEY = _required_env('SECRET_KEY', 'zelzal-dev-secret-key')
    JWT_SECRET_KEY = _required_env('JWT_SECRET_KEY', 'zelzal-dev-jwt-secret')
    SQLALCHEMY_DATABASE_URI = _required_env('DATABASE_URL', 'sqlite:///zelzal.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = '100/hour'
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
