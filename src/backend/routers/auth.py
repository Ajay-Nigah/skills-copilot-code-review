"""
Authentication endpoints for the High School Management System API
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from typing import Dict, Any

from ..authentication import (
    SESSION_COOKIE_NAME,
    create_session,
    get_authenticated_teacher,
    revoke_session,
)
from ..database import teachers_collection, verify_password

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/login")
def login(username: str, password: str, response: Response) -> Dict[str, Any]:
    """Login a teacher account"""
    # Find the teacher in the database
    teacher = teachers_collection.find_one({"_id": username})

    # Verify password using Argon2 verifier from database.py
    if not teacher or not verify_password(teacher.get("password", ""), password):
        raise HTTPException(
            status_code=401, detail="Invalid username or password")

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=create_session(teacher["username"]),
        max_age=30 * 24 * 60 * 60,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/",
    )
    return {
        "username": teacher["username"],
        "display_name": teacher["display_name"],
        "role": teacher["role"],
    }


@router.get("/check-session")
def check_session(
    teacher: Dict[str, Any] = Depends(get_authenticated_teacher),
) -> Dict[str, Any]:
    """Check a signed-in teacher's session."""
    return teacher


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    _: Dict[str, Any] = Depends(get_authenticated_teacher),
) -> Dict[str, str]:
    """Revoke the current teacher session."""
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    revoke_session(token)
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/",
    )
    return {"message": "Logged out"}
