from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db

router = APIRouter(prefix="/tracks", tags=["tracks"])


class TrackOut(BaseModel):
    track_id: int
    name: str
    album_id: int
    album_title: Optional[str] = None
    artist_id: Optional[int] = None
    artist_name: Optional[str] = None
    media_type_id: int
    media_type: Optional[str] = None
    genre_id: Optional[int] = None
    genre: Optional[str] = None
    composer: Optional[str] = None
    milliseconds: int
    bytes: Optional[int] = None
    unit_price: float


class AudioPreviewOut(BaseModel):
    track_id: int
    message: str
    note: str


@router.get("", response_model=list[TrackOut])
def list_tracks(
    q: Optional[str] = Query(default=None, description="Search by track name"),
    album_id: Optional[int] = Query(default=None),
    artist_id: Optional[int] = Query(default=None),
    genre_id: Optional[int] = Query(default=None),
    media_type_id: Optional[int] = Query(default=None),
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    sql = """
        SELECT
            t.TrackId AS track_id,
            t.Name AS name,
            t.AlbumId AS album_id,
            a.Title AS album_title,
            ar.ArtistId AS artist_id,
            ar.Name AS artist_name,
            t.MediaTypeId AS media_type_id,
            mt.Name AS media_type,
            t.GenreId AS genre_id,
            g.Name AS genre,
            t.Composer AS composer,
            t.Milliseconds AS milliseconds,
            t.Bytes AS bytes,
            t.UnitPrice AS unit_price
        FROM Track t
        JOIN Album a ON a.AlbumId = t.AlbumId
        JOIN Artist ar ON ar.ArtistId = a.ArtistId
        JOIN MediaType mt ON mt.MediaTypeId = t.MediaTypeId
        LEFT JOIN Genre g ON g.GenreId = t.GenreId
    """

    where = []
    params = {"limit": limit, "offset": offset}

    if q:
        where.append("t.Name LIKE :q")
        params["q"] = f"%{q}%"

    if album_id is not None:
        where.append("t.AlbumId = :album_id")
        params["album_id"] = album_id

    if artist_id is not None:
        where.append("ar.ArtistId = :artist_id")
        params["artist_id"] = artist_id

    if genre_id is not None:
        where.append("t.GenreId = :genre_id")
        params["genre_id"] = genre_id

    if media_type_id is not None:
        where.append("t.MediaTypeId = :media_type_id")
        params["media_type_id"] = media_type_id

    if min_price is not None:
        where.append("t.UnitPrice >= :min_price")
        params["min_price"] = min_price

    if max_price is not None:
        where.append("t.UnitPrice <= :max_price")
        params["max_price"] = max_price

    if where:
        sql += " WHERE " + " AND ".join(where)

    sql += " ORDER BY t.Name LIMIT :limit OFFSET :offset"

    rows = db.execute(text(sql), params).mappings().all()
    return [TrackOut(**dict(r)) for r in rows]


@router.get("/{track_id}", response_model=TrackOut)
def get_track(track_id: int, db: Session = Depends(get_db)):
    row = db.execute(
        text(
            """
            SELECT
                t.TrackId AS track_id,
                t.Name AS name,
                t.AlbumId AS album_id,
                a.Title AS album_title,
                ar.ArtistId AS artist_id,
                ar.Name AS artist_name,
                t.MediaTypeId AS media_type_id,
                mt.Name AS media_type,
                t.GenreId AS genre_id,
                g.Name AS genre,
                t.Composer AS composer,
                t.Milliseconds AS milliseconds,
                t.Bytes AS bytes,
                t.UnitPrice AS unit_price
            FROM Track t
            JOIN Album a ON a.AlbumId = t.AlbumId
            JOIN Artist ar ON ar.ArtistId = a.ArtistId
            JOIN MediaType mt ON mt.MediaTypeId = t.MediaTypeId
            LEFT JOIN Genre g ON g.GenreId = t.GenreId
            WHERE t.TrackId = :track_id
            """
        ),
        {"track_id": track_id},
    ).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Track not found")

    return TrackOut(**dict(row))


@router.get("/{track_id}/audio-preview", response_model=AudioPreviewOut)
def audio_preview(track_id: int, db: Session = Depends(get_db)):
    # Just verify track exists for now
    exists = db.execute(
        text("SELECT 1 FROM Track WHERE TrackId = :track_id"),
        {"track_id": track_id},
    ).first()

    if not exists:
        raise HTTPException(status_code=404, detail="Track not found")

    return AudioPreviewOut(
        track_id=track_id,
        message="Audio preview is not implemented yet.",
        note="This endpoint is a placeholder for future streaming features.",
    )
