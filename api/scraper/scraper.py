import requests
from bs4 import BeautifulSoup
import json
from ..models.pydantic_models import FlixListRequestModel, FlixDetailsRequestModel
import datetime
from typing import Dict, List, Optional
import logging

class WebScraperError(Exception):
    pass

class NetworkError(WebScraperError):
    pass

class ParsingError(WebScraperError):
    pass
# TODO: Consider encrypting or rotating sensitive headers such as 'cookie'.
HEADERS = {
    'authority': 'flixpatrol.com',
    'method': 'GET',
    'path': '/top10/netflix/world/2023-038/full/',
    'scheme': 'https',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,la;q=0.8',
    'Cache-Control': 'max-age=0',
    'Cookie': 'flixpatrol=cf84f3c127a7449edf7df88eec331cbe; _gid=GA1.2.1605022267.1695758290; userid=n12fvnax87jg8cgn; _ga_CW5LDBFGF5=GS1.1.1695758290.39.1.1695763521.0.0.0; _ga=GA1.1.1758190770.1677534659',
    'Sec-Ch-Ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}


def get_last_week():
    today = datetime.date.today()
    year = today.strftime('%Y')  # Get the current year as string
    week_number = today.isocalendar()[1] - 1  # Get week number and subtract 1

    # Handle edge case: If week_number becomes 0 (i.e., the last week of the previous year)
    if week_number == 0:
        year = str(int(year) - 1)  # Reduce the year by 1
        week_number = 52  # ISO week numbering could be either 52 or 53 weeks, but for simplicity, we're using 52.
    print(f"{year}-{week_number:03}")
    return f"{year}-{week_number:03}"  # Format the week number to have leading zeros

def get_response(url: str):

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        raise NetworkError(f"Error fetching URL: {e}")

def scrape_titles(params: FlixListRequestModel):
    week_date = get_last_week()
    url = f"https://flixpatrol.com/top10/{params.platform}/world/{week_date}/full/"
    response = get_response(url)
    
    try:
        soup = BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        raise ParsingError(f"Error parsing HTML content: {e}")

    # Find the div with specified ID
    div = soup.find('div', {'id': f"{params.platform}-{params.media_type_value()}"})

    # Create a list to store the title objects
    titles_list = []

    # Extract the title and details_url from the list
    if div:
        title_elements = div.find_all(['a', 'h3'])  # Search for both 'a' and 'h3' tags

        # Check for "Official" tab
        official_tab = div.find('a', text='Official')

        skip_count = 3 if official_tab else 2

        for index, title_elem in enumerate(title_elements, start=1):
            # Skip based on presence or absence of "Official" tab
            if index > skip_count:
                title = title_elem.text
                details_url = "https://flixpatrol.com" + title_elem.get('href') if title_elem.name == 'a' else None
                title_obj = {
                    "rank": index - skip_count,  # Adjust rank based on skip_count
                    "title": title,
                    "details_url": details_url
                }
                titles_list.append(title_obj)

    return {
        "platform": params.platform,  # use the name attribute
        "media_type": params.media_type,  # use the name attribute
        "media_list": titles_list
    }


def get_page_content(url: str) -> str:
    try:
        response = get_response(url)
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        logging.error(f"Error in get_page_content for URL {url}: {e}")
        raise ParsingError(f"Error in get_page_content: {e}")

def extract_json_data(soup: BeautifulSoup) -> Dict:
    try:
        script_content = soup.find('script', type="application/ld+json").string
        return json.loads(script_content)
    except Exception as e:
        logging.error(f"Error in extract_json_data: {e}")
        raise ParsingError(f"Error in extract_json_data: {e}")

def extract_overview(soup: BeautifulSoup) -> str:
    try:
        overview_div = soup.select_one("div.card-body")
        return overview_div.get_text().strip() if overview_div else None
    except Exception as e:
        logging.error(f"Error in extract_overview: {e}")
        raise ParsingError(f"Error in extract_overview: {e}")

def extract_actors(soup: BeautifulSoup) -> List[str]:
    try:
        starring_div = soup.find("div", string="STARRING")
        if starring_div:
            actors_div = starring_div.find_next_sibling("div")
            if actors_div:
                return [actor.strip() for actor in actors_div.get_text().split(',')]
        return []
    except Exception as e:
        logging.error(f"Error in extract_actors: {e}")
        raise ParsingError(f"Error in extract_actors: {e}")

def extract_rating(soup: BeautifulSoup, keyword: str) -> Optional[float]:
    try:
        rating_div = soup.find("div", string=keyword)
        if rating_div:
            score_div = rating_div.find_previous_sibling("div")
            if score_div:
                rating_text = score_div.get_text().split('/')[0].strip()
                return float(rating_text)
        return None
    except ValueError as e:
        logging.error(f"ValueError in extract_rating for keyword {keyword}: {e}")
        return None
    except Exception as e:
        logging.error(f"Error in extract_rating for keyword {keyword}: {e}")
        raise ParsingError(f"Error in extract_rating: {e}")

def extract_info_spans(soup: BeautifulSoup) -> List[str]:
    try:
        info_div = soup.select_one("div.flex.flex-wrap.text-sm.leading-6.text-gray-500")
        info_spans = []
        if info_div:
            spans_list = info_div.find_all("span")
            for span in spans_list:
                span_text = span.get_text(strip=True)
                if ('|' not in span_text 
                    and not any(char.isdigit() for char in span_text) 
                    and span_text != "Movie" 
                    and span_text != "Tv Show"
                    and span.get('title') is None):
                    info_spans.append(span_text.lower())
        return info_spans
    except Exception as e:
        logging.error(f"Error in extract_info_spans: {e}")
        raise ParsingError(f"Error in extract_info_spans: {e}")

def extract_slug(url: str) -> str:
    try:
        return str(url).rstrip('/').split("title/")[-1]
    except Exception as e:
        logging.error(f"Error in extract_slug for URL {url}: {e}")
        raise ParsingError(f"Error in extract_slug: {e}")
   
def scrape_details(params: FlixDetailsRequestModel):
    try:
        soup = get_page_content(params.details_url)
        data = extract_json_data(soup)
        overview = extract_overview(soup)
        actors = extract_actors(soup)
        imdb_rating = extract_rating(soup, "imdb")
        rt_rating = extract_rating(soup, "rotten tomatoes")
        info_spans = extract_info_spans(soup)
        slug = extract_slug(params.details_url)
    except Exception as e:
        raise ParsingError(f"Error processing scraped details: {e}")
    
    imdb_id = None if not data.get("sameAs") else next((x.split("/")[-2] for x in data["sameAs"] if "imdb.com" in x), None)
    if not imdb_id:
        return {
        "title": data.get("name"),
        "year": 2010,
        "ids": {
            "trakt": None,
            "slug": "titanic-2",
            "imdb": "tt1640571",
            "tmdb": None
        },
        "tagline": None,
        "overview": "On the 100th anniversary of the original voyage, a modern luxury liner christened \\Titanic 2,\\ follows the path of its namesake. But when a tsunami hurls an ice berg into the new ship's path, the passengers and crew must fight to avoid a similar fate.",
        "released": "2010-08-07",
        "runtime": None,
        "country": "united states",
        "updated_at": None,
        "trailer": None,
        "homepage": None,
        "status": None,
        "rating": {
            "imdb": 1.6,
            "rt": None
        },
        "votes": None,
        "comment_count": None,
        "language": None,
        "available_translations": None,
        "genres": ["action"],
        "certification": None,
        "directors": ["Shane Van Dyke"],
        "actors": ["Shane Van Dyke"],
        "art": {
            "flix_cover": "https://flixpatrol.com/runtime/cache/files/posters/t/tusmxx60dgktioidnunnrjltp3t.webp",
            "logo": None,
            "poster": None,
            "background": None,
            "banner": None,
            "thumbs": None
        }
    }
        
    details = {
        "title": data.get("name"),
        "year": int(data.get("dateCreated").split("-")[0]) if data.get("dateCreated") else None,
        "ids": {
            "trakt": None,
            "slug": slug,
            "imdb": imdb_id,
            "tmdb": None if not data.get("sameAs") else next((int(x.split("/")[-1]) for x in data["sameAs"] if "themoviedb.org" in x), None)
        },
        "tagline": None,
        "overview": overview,
        "released": data.get("dateCreated"),
        "runtime": None,
        "country": info_spans[0] if info_spans else None,
        "updated_at": None,
        "trailer": None,
        "homepage": None,
        "status": None,
        "rating": {
            "imdb": imdb_rating,
            "rt": rt_rating
        },
        "votes": None,
        "comment_count": None,
        "language": None,
        "available_translations": None,
        "genres": info_spans[1:] if info_spans else [],
        "certification": None,
        "directors": [director.get("name") for director in data.get("directors", [])] if data.get("directors") else [],
        "actors": actors,
        "art": {
            "flix_cover": data.get("image"),
            "logo": None,
            "poster": None,
            "background": None,
            "banner": None,
            "thumbs": None
        }
    }

    return details
