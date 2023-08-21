from fastapi import APIRouter, HTTPException
from ..models.pydantic_models import FlixListRequestModel, FlixListResponseModel, FlixDetailsRequestModel
from ..scraper.scraper import scrape_details, scrape_titles, NetworkError, ParsingError

router = APIRouter()

@router.get("/scrape/flixlist/", response_model=FlixListResponseModel)
async def scrape_full_flixlist(media_type: str, platform: str):
    params = FlixListRequestModel(media_type=media_type, platform=platform)
    try:
        titles = scrape_titles(params)
        if not titles or not titles.get('media_list'):
            raise HTTPException(status_code=404, detail="Failed to scrape the data")
        return titles
    except (NetworkError, ParsingError) as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scrape/details/")
async def scrape_media_details(details_url: str):
    params = FlixDetailsRequestModel(details_url=details_url)
    try:
        details_data = scrape_details(params)
        return details_data
    except (NetworkError, ParsingError) as e:
        raise HTTPException(status_code=500, detail=str(e))
