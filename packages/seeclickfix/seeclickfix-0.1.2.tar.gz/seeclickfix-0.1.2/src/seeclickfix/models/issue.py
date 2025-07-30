from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class Errors(BaseModel):
    pass


class Media(BaseModel):
    video_url: Optional[None]
    representative_image_url: str
    image_full: Optional[str] = None
    image_square_100_x100: Optional[str] = None


class Status(str, Enum):
    ACKNOWLEDGED = "Acknowledged"
    CLOSED = "Closed"
    OPEN = "Open"


class Issue(BaseModel):
    id: int
    status: str
    summary: str
    description: str
    lat: float
    lng: float
    address: str
    created_at: str
    url: str
    media: Media
    rating: Optional[int] = None
    acknowledged_at: Optional[str] = None
    closed_at: Optional[str] = None
    reopened_at: Optional[str] = None
    shortened_url: Optional[str] = None


class Pagination(BaseModel):
    entries: int
    page: int
    per_page: int
    pages: int
    next_page: int
    next_page_url: str
    previous_page: Optional[int] = None
    previous_page_url: Optional[str] = None


class Metadata(BaseModel):
    pagination: Pagination


class RootObject(BaseModel):
    issues: List[Issue]
    metadata: Metadata
    errors: Errors
