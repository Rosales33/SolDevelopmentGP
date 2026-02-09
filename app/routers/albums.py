from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db

router = APIRouter(prefix="/albums", tags=["albums"])


class AlbumOut(BaseModel):
    album_id: int
    title: str
    artist_id: int
    artist_name: Optional[str] = None


class TrackOut(BaseModel):
    track_id: int
    name: str
    album_id: int
    media_type_id: int
    genre_id: Optional[int] = None
    composer: Optional[str] = None
    milliseconds: int
    bytes: Optional[int] = None
    unit_price: float


@router.get("", response_model=list[AlbumOut])
def list_albums(
    q: Optional[str] = Query(default=None, description="Search by album title"),
    artist_id: Optional[int] = Query(default=None, description="Filter by artist id"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    base_sql = """
        SELECT
            a.AlbumId  AS album_id,
            a.Title    AS title,
            a.ArtistId AS artist_id,
            ar.Name    AS artist_name
        FROM Album a
        JOIN Artist ar ON ar.ArtistId = a.ArtistId
    """

    where = []
    params = {"limit": limit, "offset": offset}

    if q:
        where.append("a.Title LIKE :q")
        params["q"] = f"%{q}%"

    if artist_id is not None:
        where.append("a.ArtistId = :artist_id")
        params["artist_id"] = artist_id

    if where:
        base_sql += " WHERE " + " AND ".join(where)

    base_sql += " ORDER BY a.Title LIMIT :limit OFFSET :offset"

    rows = db.execute(text(base_sql), params).mappings().all()
    return [AlbumOut(**dict(r)) for r in rows]


@router.get("/{album_id}", response_model=AlbumOut)
def get_album(album_id: int, db: Session = Depends(get_db)):
    row = db.execute(
        text(
            """
            SELECT
                a.AlbumId  AS album_id,
                a.Title    AS title,
                a.ArtistId AS artist_id,
                ar.Name    AS artist_name
            FROM Album a
            JOIN Artist ar ON ar.ArtistId = a.ArtistId
            WHERE a.AlbumId = :album_id
            """
        ),
        {"album_id": album_id},
    ).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Album not found")

    return AlbumOut(**dict(row))


@router.get("/{album_id}/tracks", response_model=list[TrackOut])
def list_album_tracks(
    album_id: int,
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    # Ensure album exists
    exists = db.execute(
        text("SELECT 1 FROM Album WHERE AlbumId = :album_id"),
        {"album_id": album_id},
    ).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Album not found")

    rows = db.execute(
        text(
            """
            SELECT
                TrackId     AS track_id,
                Name        AS name,
                AlbumId     AS album_id,
                MediaTypeId AS media_type_id,
                GenreId     AS genre_id,
                Composer    AS composer,
                Milliseconds AS milliseconds,
                Bytes       AS bytes,
                UnitPrice   AS unit_price
            FROM Track
            WHERE AlbumId = :album_id
            ORDER BY Name
            LIMIT :limit OFFSET :offset
            """
        ),
        {"album_id": album_id, "limit": limit, "offset": offset},
    ).mappings().all()

    return [TrackOut(**dict(r)) for r in rows]
