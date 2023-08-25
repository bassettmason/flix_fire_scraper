from pydantic import BaseModel, HttpUrl
from typing import List, Literal, Optional, Union


class MediaListItem(BaseModel):
    rank: int
    title: str
    details_url: HttpUrl


class FlixListRequestModel(BaseModel):
    media_type: Literal["movie", "show"]
    platform: Literal["netflix", "hbo", "paramount-plus", "hulu", "amazon-prime", "disney"]

    def media_type_value(self):
        media_type_map = {
            "movie": "1",
            "show": "2"
        }
        return media_type_map.get(self.media_type, self.media_type)


class FlixListResponseModel(BaseModel):
    platform: Literal["netflix", "hbo", "paramount-plus", "hulu", "amazon-prime", "disney"]
    media_type: Literal["movie", "show"]
    media_list: List[MediaListItem]


class IDS(BaseModel):
    trakt: Optional[Union[int, str]]  # Assuming this can be either int or str, but can be adjusted
    slug: str
    imdb: str
    tmdb: int


class Rating(BaseModel):
    imdb: float
    rt: Optional[float]


class Art(BaseModel):
    flix_cover: HttpUrl
    logo: Optional[HttpUrl]
    poster: Optional[HttpUrl]
    background: Optional[HttpUrl]
    banner: Optional[HttpUrl]
    thumbs: Optional[HttpUrl]


class MediaDetailsResponseModel(BaseModel):
    title: str
    year: int
    ids: IDS
    tagline: Optional[str]
    overview: str
    released: str
    runtime: Optional[int]
    country: str
    updated_at: Optional[str]
    trailer: Optional[HttpUrl]
    homepage: Optional[HttpUrl]
    status: Optional[str]
    rating: Rating
    votes: Optional[int]
    comment_count: Optional[int]
    language: Optional[str]
    available_translations: Optional[List[str]]
    genres: List[str]
    certification: Optional[str]
    directors: List[str]
    actors: List[str]
    art: Art

class FlixDetailsRequestModel(BaseModel):
    details_url: HttpUrl
