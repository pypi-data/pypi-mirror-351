from pydantic import BaseModel
from typing import Optional, List

# --- Secondary Schemas ---
# Same as the first schemas.py file

class RatingBase(BaseModel):
    userId: int
    movieId: int
    rating: float
    timestamp: int

    class Config:
        orm_mode = True


class TagBase(BaseModel):
    userId: int
    movieId: int
    tag: str
    timestamp: int

    class Config:
        orm_mode = True


class LinkBase(BaseModel):
    imdbId: Optional[str]
    tmdbId: Optional[int]

    class Config:
        orm_mode = True


# --- Main Movie Schema ---
class MovieBase(BaseModel):
    movieId: int
    title: str
    genres: Optional[str] = None

    class Config:
        orm_mode = True


class MovieDetailed(MovieBase):
    ratings: List[RatingBase] = []
    tags: List[TagBase] = []
    link: Optional[LinkBase] = None


# --- Movie list schema (without nested details) ---
class MovieSimple(BaseModel):
    movieId: int
    title: str
    genres: Optional[str]

    class Config:
        orm_mode = True


# --- For standalone /ratings and /tags endpoints ---
class RatingSimple(BaseModel):
    userId: int
    movieId: int
    rating: float
    timestamp: int

    class Config:
        orm_mode = True


class TagSimple(BaseModel):
    userId: int
    movieId: int
    tag: str
    timestamp: int

    class Config:
        orm_mode = True


class LinkSimple(BaseModel):
    movieId: int
    imdbId: Optional[str]
    tmdbId: Optional[int]

    class Config:
        orm_mode = True


class AnalyticsResponse(BaseModel):
    movie_count: int
    rating_count: int
    tag_count: int
    link_count: int

    class Config:
        orm_mode = True