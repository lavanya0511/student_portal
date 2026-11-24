import secrets
import hmac
from fastapi import Request


def get_csrf_token(request: Request) -> str:
    token = request.session.get("csrf_token")

    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token

    return token


def valid_csrf_token(
    request: Request,
    submitted_token: str) -> bool:
    saved_token = request.session.get("csrf_token")

    if not saved_token or not submitted_token:
        return False

    return hmac.compare_digest(
        saved_token,
        submitted_token)