import hashlib
import secrets

from flask import current_app

from ..extensions import db
from ..models.api_token import ApiToken


def create_api_token_for_user(user):
    raw_token = secrets.token_urlsafe(32)
    token_hash = _hash_token(raw_token)
    record = ApiToken(token_hash=token_hash, user=user)
    db.session.add(record)
    db.session.commit()
    return raw_token


def get_user_by_token(raw_token):
    token_hash = _hash_token(raw_token)
    record = ApiToken.query.filter_by(token_hash=token_hash).first()
    return record.user if record else None


def _hash_token(raw_token):
    salt = current_app.config["API_TOKEN_SALT"]
    value = f"{salt}:{raw_token}".encode("utf-8")
    return hashlib.sha256(value).hexdigest()
