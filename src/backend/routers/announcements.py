"""Announcement endpoints."""

from datetime import date
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..authentication import get_authenticated_teacher
from ..database import announcements_collection
from ..school_time import school_today

router = APIRouter(prefix="/announcements", tags=["announcements"])


class AnnouncementInput(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    expiration_date: date
    start_date: Optional[date] = None


def serialize_announcement(announcement: Dict[str, Any]) -> Dict[str, Any]:
    """Return an announcement with its database ID exposed as `id`."""
    return {
        "id": announcement["_id"],
        "message": announcement["message"],
        "start_date": announcement.get("start_date"),
        "expiration_date": announcement["expiration_date"],
    }


def validate_announcement_dates(
    start_date: Optional[date],
    expiration_date: date,
) -> None:
    if start_date and start_date > expiration_date:
        raise HTTPException(
            status_code=422,
            detail="Start date must be on or before the expiration date",
        )


@router.get("/active", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    """Get announcements that are currently within their date range."""
    today = school_today().isoformat()
    announcements = announcements_collection.find({
        "expiration_date": {"$gte": today},
        "$or": [
            {"start_date": None},
            {"start_date": {"$lte": today}},
        ],
    }).sort("expiration_date", 1)
    return [serialize_announcement(item) for item in announcements]


@router.get("/today", response_model=Dict[str, str])
def get_school_date() -> Dict[str, str]:
    """Get the current date in the configured school timezone."""
    return {"today": school_today().isoformat()}


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
def get_announcements(
    _: Dict[str, Any] = Depends(get_authenticated_teacher),
) -> List[Dict[str, Any]]:
    """List all announcements for a signed-in teacher."""
    announcements = announcements_collection.find().sort("expiration_date", 1)
    return [serialize_announcement(item) for item in announcements]


@router.post("", response_model=Dict[str, Any], status_code=201)
@router.post("/", response_model=Dict[str, Any], status_code=201)
def create_announcement(
    announcement: AnnouncementInput,
    _: Dict[str, Any] = Depends(get_authenticated_teacher),
) -> Dict[str, Any]:
    """Create an announcement for a signed-in teacher."""
    message = announcement.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be blank")
    validate_announcement_dates(
        announcement.start_date,
        announcement.expiration_date,
    )

    record = {
        "_id": str(uuid4()),
        "message": message,
        "start_date": (
            announcement.start_date.isoformat()
            if announcement.start_date else None
        ),
        "expiration_date": announcement.expiration_date.isoformat(),
    }
    announcements_collection.insert_one(record)
    return serialize_announcement(record)


@router.put("/{announcement_id}", response_model=Dict[str, Any])
def update_announcement(
    announcement_id: str,
    announcement: AnnouncementInput,
    _: Dict[str, Any] = Depends(get_authenticated_teacher),
) -> Dict[str, Any]:
    """Replace an announcement for a signed-in teacher."""
    message = announcement.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be blank")
    validate_announcement_dates(
        announcement.start_date,
        announcement.expiration_date,
    )

    record = {
        "message": message,
        "start_date": (
            announcement.start_date.isoformat()
            if announcement.start_date else None
        ),
        "expiration_date": announcement.expiration_date.isoformat(),
    }
    result = announcements_collection.update_one(
        {"_id": announcement_id},
        {"$set": record},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"id": announcement_id, **record}


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: str,
    _: Dict[str, Any] = Depends(get_authenticated_teacher),
) -> Dict[str, str]:
    """Delete an announcement for a signed-in teacher."""
    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"message": "Announcement deleted"}
