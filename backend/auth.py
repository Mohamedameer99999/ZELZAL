import re
import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from models import User

BLOCKLIST = set()


def add_to_blocklist(jti: str):
    BLOCKLIST.add(jti)


def is_jti_blocklisted(jti: str) -> bool:
    return jti in BLOCKLIST


def sanitize_input(text: str) -> str:
    if not isinstance(text, str):
        return text
    text = text.strip()
    text = re.sub(r'[<>\'"]', '', text)
    return text[:500]


def is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def create_user(username: str, email: str, password: str, role: str = 'user') -> User:
    user = User(
        username=username.strip(),
        email=email.strip().lower(),
        password_hash=hash_password(password),
        role=role,
    )
    return user


def authenticate_user(db_session, username: str, password: str):
    user = db_session.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    if user and check_password(password, user.password_hash):
        return user
    return None


def generate_tokens(user: User):
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            'username': user.username,
            'role': user.role,
            'email': user.email,
        }
    )
    refresh_token = create_refresh_token(identity=user.id)
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict(),
    }
