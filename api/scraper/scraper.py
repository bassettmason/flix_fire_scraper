import requests
from bs4 import BeautifulSoup
import json
from ..models.pydantic_models import FlixListRequestModel, FlixDetailsRequestModel
import datetime
from typing import Dict, List, Optional
# TODO: do logging
class WebScraperError(Exception):
    pass

class NetworkError(WebScraperError):
    pass

class ParsingError(WebScraperError):
    pass
# TODO: Consider encrypting or rotating sensitive headers such as 'cookie'.
HEADERS = {
    'authority': 'flixpatrol.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,la;q=0.8',
    'cache-control': 'max-age=0',
    'cookie': '_nss=1; _ga=GA1.2.1758190770.1677534659; _gid=GA1.2.1944429410.1681412121; _gat_gtag_UA_2491325_22=1',
    'referer': 'https://flixpatrol.com/top10/',
    'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': 'Windows',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
}
def get_last_week():
    today = datetime.date.today()
    year = today.strftime('%Y')  # Get the current year as string
    week_number = today.isocalendar()[1] - 1  # Get week number and subtract 1

    # Handle edge case: If week_number becomes 0 (i.e., the last week of the previous year)
    if week_number == 0:
        year = str(int(year) - 1)  # Reduce the year by 1
        week_number = 52  # ISO week numbering could be either 52 or 53 weeks, but for simplicity, we're using 52.

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
        for index, title_elem in enumerate(title_elements, start=1):
            # Skip the first two titles
            if index > 3:
                title = title_elem.text
                details_url = "https://flixpatrol.com" + title_elem.get('href') if title_elem.name == 'a' else None
                title_obj = {
                    "rank": index - 3,  # Subtract 3 from index to exclude non-titles
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
    response = get_response(url)
    return BeautifulSoup(response.content, 'html.parser')

def extract_json_data(soup: BeautifulSoup) -> Dict:
    script_content = soup.find('script', type="application/ld+json").string
    return json.loads(script_content)

def extract_overview(soup: BeautifulSoup) -> str:
    overview_div = soup.select_one("div.card-body")
    return overview_div.get_text().strip() if overview_div else None

def extract_actors(soup: BeautifulSoup) -> List[str]:
    starring_div = soup.find("div", string="STARRING")
    if starring_div:
        actors_div = starring_div.find_next_sibling("div")
        if actors_div:
            return [actor.strip() for actor in actors_div.get_text().split(',')]
    return []

def extract_rating(soup: BeautifulSoup, keyword: str) -> Optional[float]:
    rating_div = soup.find("div", string=keyword)
    if rating_div:
        score_div = rating_div.find_previous_sibling("div")
        if score_div:
            rating_text = score_div.get_text().split('/')[0].strip()
            try:
                return float(rating_text)
            except ValueError:
                return None
    return None

def extract_info_spans(soup: BeautifulSoup) -> List[str]:
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

def extract_slug(url: str) -> str:
    return str(url).rstrip('/').split("title/")[-1]

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
    details = {
        "title": data.get("name"),
        "year": int(data.get("dateCreated").split("-")[0]) if data.get("dateCreated") else None,
        "ids": {
            "trakt": None,
            "slug": slug,
            "imdb": None if not data.get("sameAs") else next((x.split("/")[-2] for x in data["sameAs"] if "imdb.com" in x), None),
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
