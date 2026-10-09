"""
Authentication endpoints for the High School Management System API
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Dict, Any

from ..authentication import create_session, get_authenticated_teacher, revoke_session
from ..database import teachers_collection, verify_password

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)
bearer_scheme = HTTPBearer(auto_error=False)


@router.post("/login")
def login(username: str, password: str) -> Dict[str, Any]:
    """Login a teacher account"""
    # Find the teacher in the database
    teacher = teachers_collection.find_one({"_id": username})

    # Verify password using Argon2 verifier from database.py
    if not teacher or not verify_password(teacher.get("password", ""), password):
        raise HTTPException(
            status_code=401, detail="Invalid username or password")

    # Return teacher information (excluding password)
    return {
        "username": teacher["username"],
        "display_name": teacher["display_name"],
        "role": teacher["role"],
        "session_token": create_session(teacher["username"]),
    }


@router.get("/check-session")
def check_session(
    teacher: Dict[str, Any] = Depends(get_authenticated_teacher),
) -> Dict[str, Any]:
    """Check a signed-in teacher's session."""
    return teacher


@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    _: Dict[str, Any] = Depends(get_authenticated_teacher),
) -> Dict[str, str]:
    """Revoke the current teacher session."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    revoke_session(credentials.credentials)
    return {"message": "Logged out"}
