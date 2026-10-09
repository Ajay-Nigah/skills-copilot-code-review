"""Authentication helpers for protected API endpoints."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from fastapi import Depends, HTTPException, Request

from .database import sessions_collection, teachers_collection

SESSION_COOKIE_NAME = "teacher_session"


def create_session(username: str) -> str:
    """Create a revocable, time-limited bearer token for a teacher."""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    sessions_collection.insert_one({
        "_id": hashlib.sha256(token.encode()).hexdigest(),
        "username": username,
        "expires_at": expires_at,
    })
    return token


def revoke_session(token: str) -> None:
    """Remove a session token from the database."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    sessions_collection.delete_one({"_id": token_hash})


def get_authenticated_teacher(
    request: Request,
) -> Dict[str, Any]:
    """Return the teacher for a valid session cookie or raise 401."""
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    session = sessions_collection.find_one({
        "_id": token_hash,
        "expires_at": {"$gt": datetime.now(timezone.utc)},
    })
    if session is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    teacher = teachers_collection.find_one({"_id": session["username"]})
    if teacher is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return {
        "username": teacher["username"],
        "display_name": teacher["display_name"],
        "role": teacher["role"],
    }
