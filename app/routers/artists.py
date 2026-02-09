from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db

router = APIRouter(prefix="/artists", tags=["artists"])


class ArtistOut(BaseModel):
    artist_id: int
    name: Optional[str] = None


class AlbumOut(BaseModel):
    album_id: int
    title: str
    artist_id: int


@router.get("", response_model=list[ArtistOut])
def list_artists(
    q: Optional[str] = Query(default=None, description="Search by artist name"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    if q:
        rows = db.execute(
            text(
                """
                SELECT ArtistId AS artist_id, Name AS name
                FROM Artist
                WHERE Name LIKE :q
                ORDER BY Name
                LIMIT :limit OFFSET :offset
                """
            ),
            {"q": f"%{q}%", "limit": limit, "offset": offset},
        ).mappings().all()
    else:
        rows = db.execute(
            text(
                """
                SELECT ArtistId AS artist_id, Name AS name
                FROM Artist
                ORDER BY Name
                LIMIT :limit OFFSET :offset
                """
            ),
            {"limit": limit, "offset": offset},
        ).mappings().all()

    return [ArtistOut(**dict(r)) for r in rows]


@router.get("/{artist_id}", response_model=ArtistOut)
def get_artist(artist_id: int, db: Session = Depends(get_db)):
    row = db.execute(
        text(
            """
            SELECT ArtistId AS artist_id, Name AS name
            FROM Artist
            WHERE ArtistId = :artist_id
            """
        ),
        {"artist_id": artist_id},
    ).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Artist not found")

    return ArtistOut(**dict(row))


@router.get("/{artist_id}/albums", response_model=list[AlbumOut])
def list_artist_albums(
    artist_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    # ensure artist exists
    exists = db.execute(
        text("SELECT 1 FROM Artist WHERE ArtistId = :artist_id"),
        {"artist_id": artist_id},
    ).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Artist not found")

    rows = db.execute(
        text(
            """
            SELECT AlbumId AS album_id, Title AS title, ArtistId AS artist_id
            FROM Album
            WHERE ArtistId = :artist_id
            ORDER BY Title
            LIMIT :limit OFFSET :offset
            """
        ),
        {"artist_id": artist_id, "limit": limit, "offset": offset},
    ).mappings().all()

    return [AlbumOut(**dict(r)) for r in rows]
