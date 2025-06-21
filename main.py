from fastapi import FastAPI, HTTPException, Query
from bs4 import BeautifulSoup
import requests
import re
import ast
from json import load

app = FastAPI(
    title="MyInstants API",
    description="API for accessing MyInstants sound library with scraping capabilities",
    version="1.0",
    docs_url="/",
    openapi_tags=[
        {
            "name": "Sound Discovery",
            "description": "Endpoints for discovering trending and popular sounds"
        },
        {
            "name": "User Content",
            "description": "Operations related to user profiles and content"
        },
        {
            "name": "Sound Details",
            "description": "Get detailed information about specific sounds"
        },
        {
            "name": "Search Operations",
            "description": "Search sounds across the platform"
        }
    ]
)

BASE_URL = "https://www.myinstants.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

with open('responses_formats.json', 'r', encoding='utf-8') as f:
    responses_formats: dict = load(f)

def fetch_html(url: str):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException:
        return None

def extract_play_args(onclick_str):
    try:
        start = onclick_str.index('(') + 1
        end = onclick_str.rindex(')')
        args_str = onclick_str[start:end]
        return list(ast.literal_eval(f'({args_str})'))
    except (ValueError, SyntaxError, TypeError):
        return []


def parse_sounds(html_content: str):
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    sounds = []

    for instant in soup.find_all("div", class_="instant"):
        link = instant.find("a", class_="instant-link")
        if not link:
            continue

        title = link.get_text(strip=True)
        path = link.get('href', '')
        sound_id = path.split('/')[-2] if path else ''

        button = instant.find("button", class_="small-button")
        if button and button.get('onclick'):
            onclick = button['onclick']
            args = extract_play_args(onclick)
            if not args:
                continue
            mp3_path = args[0]

            sounds.append({
                "id": sound_id,
                "title": title,
                "url": f"{BASE_URL}{path}",
                "mp3": f"{BASE_URL}{mp3_path}"
            })

    return sounds

@app.get("/trending",
         tags=["Sound Discovery"],
         summary="Get trending sounds",
         description="Retrieve currently trending sounds based on location",
         responses={
             200: {
                 "description": "List of trending sounds",
                 "content": {
                     "application/json": {
                         "example": [responses_formats["listed_instant"]]
                     }
                 }
             },
             404: {"description": "Page not found or invalid locale"}
         })
async def trending(locale: str = Query(..., min_length=1, description="Location code (e.g. 'us', 'fr')")):
    """
    Retrieve currently trending sounds for a specific location.

    **Response Format:**
    - Array of sound objects with:
        - `id`: Unique sound identifier
        - `title`: Sound title
        - `url`: Direct link to sound page
        - `mp3`: Direct URL to MP3 file

    **Possible Errors:**
    - 404: If the locale is invalid or page not found
    """
    html = fetch_html(f"{BASE_URL}/en/index/{locale}")
    if not html:
        raise HTTPException(status_code=404, detail="Page not found")
    return parse_sounds(html)

@app.get("/favorites",
         tags=["User Content"],
         summary="Get user favorites",
         responses={
             200: {
                 "description": "List of user's favorite sounds",
                 "content": {
                     "application/json": {
                         "example": [responses_formats["listed_instant"]]
                     }
                 }
             },
             404: {"description": "User not found"}
         })
async def favorites(username: str = Query(..., min_length=1, description="MyInstants username")):
    """
    Get all sounds favorited by a specific user.

    **Response Format:**
    - Array of sound objects with:
        - `id`: Unique sound identifier
        - `title`: Sound title
        - `url`: Direct link to sound page
        - `mp3`: Direct URL to MP3 file

    **Possible Errors:**
    - 404: If username doesn't exist
    """
    html = fetch_html(f"{BASE_URL}/en/profile/{username}")
    if not html:
        raise HTTPException(status_code=404, detail="User not found")
    return parse_sounds(html)

@app.get("/detail",
         tags=["Sound Details"],
         summary="Get sound details",
         responses={
             200: {
                 "description": "Detailed sound information",
                 "content": {
                     "application/json": {
                         "example": responses_formats["detailed_instant"]
                     }
                 }
             },
             404: {"description": "Sound not found"}
         })
async def detail(id: str = Query(..., min_length=1, description="Sound ID from URL")):
    """
    Get comprehensive information about a specific sound.

    **Response Format:**
    - JSON object with:
        - `id`: Sound ID
        - `url`: Direct URL to sound page
        - `title`: Sound title
        - `mp3`: Direct MP3 URL
        - `description`: Sound description
        - `tags`: List of associated tags
        - `favorites`: Number of user favorites
        - `views`: Total view count
        - `uploader`: Uploader username
        - `uploader_url`: URL to uploader's profile

    **Possible Errors:**
    - 404: If sound ID is invalid
    """
    html = fetch_html(f"{BASE_URL}/en/instant/{id}")
    if not html:
        raise HTTPException(status_code=404, detail="Sound not found")

    soup = BeautifulSoup(html, 'html.parser')
    url = f"{BASE_URL}/en/instant/{id}"

    title = soup.find('h1', id='instant-page-title').get_text(strip=True)

    button = soup.find('button', id='instant-page-button-element')
    mp3 = BASE_URL + button.get('data-url') if button else None

    description_div = soup.find('div', id='instant-page-description')
    description = description_div.get_text(strip=True) if description_div else ''

    tags = []
    tags_div = soup.find('div', id='instant-page-tags')
    if tags_div:
        tags = [a.get_text(strip=True).replace("#", "") for a in tags_div.find_all('a')]

    # Extract favorites count
    likes_div = soup.find('div', id='instant-page-likes')
    favorites = 0
    if likes_div:
        favorites_text = likes_div.find('b').get_text(strip=True)
        favorites = int(re.search(r'\d+', favorites_text).group())

    # Extract views count
    views_text = soup.find(string=re.compile('views'))
    views = int(re.search(r'(\d+)\s*views', views_text).group(1)) if views_text else 0

    # Extract uploader info
    uploader_link = soup.find('a', href=re.compile(r'/profile/'))
    uploader = uploader_link.get_text(strip=True) if uploader_link else None
    uploader_url = f"{BASE_URL}{uploader_link['href']}" if uploader_link else None

    return {
        'id': id,
        'url': url,
        'title': title,
        'mp3': mp3,
        'description': description,
        'tags': tags,
        'favorites': favorites,
        'views': views,
        'uploader': uploader,
        'uploader_url': uploader_url
    }

@app.get("/recent",
         tags=["Sound Discovery"],
         summary="Get recently added sounds",
         responses={
             200: {
                 "description": "List of recently added sounds",
                 "content": {
                     "application/json": {
                         "example": [responses_formats["listed_instant"]]
                     }
                 }
             },
             404: {"description": "Page not found"}
         })
async def recent():
    """
    Get the most recently added sounds on MyInstants.

    **Response Format:**
    - Array of sound objects with:
        - `id`: Unique sound identifier
        - `title`: Sound title
        - `url`: Direct link to sound page
        - `mp3`: Direct URL to MP3 file

    **Possible Errors:**
    - 404: If recent sounds page is unavailable
    """
    html = fetch_html(f"{BASE_URL}/en/recent")
    if not html:
        raise HTTPException(status_code=404, detail="Page not found")
    return parse_sounds(html)

@app.get("/uploaded",
         tags=["User Content"],
         summary="Get user uploads",
         responses={
             200: {
                 "description": "List of sounds uploaded by user",
                 "content": {
                     "application/json": {
                         "example": [responses_formats["listed_instant"]]
                     }
                 }
             },
             404: {"description": "User not found"}
         })
async def uploaded(username: str = Query(..., min_length=1, description="MyInstants username")):
    """
    Get all sounds uploaded by a specific user.

    **Response Format:**
    - Array of sound objects with:
        - `id`: Unique sound identifier
        - `title`: Sound title
        - `url`: Direct link to sound page
        - `mp3`: Direct URL to MP3 file

    **Possible Errors:**
    - 404: If username doesn't exist
    """
    html = fetch_html(f"{BASE_URL}/en/profile/{username}/uploaded/")
    if not html:
        raise HTTPException(status_code=404, detail="User not found")
    return parse_sounds(html)

@app.get("/search",
         tags=["Search Operations"],
         summary="Search sounds",
         responses={
             200: {
                 "description": "List of matching sounds",
                 "content": {
                     "application/json": {
                         "example": [responses_formats["listed_instant"]]
                     }
                 }
             },
             404: {"description": "No results found"}
         })
async def search(q: str = Query(..., min_length=1, description="Search query")):
    """
    Search for sounds using keywords.

    **Response Format:**
    - Array of sound objects with:
        - `id`: Unique sound identifier
        - `title`: Sound title
        - `url`: Direct link to sound page
        - `mp3`: Direct URL to MP3 file

    **Possible Errors:**
    - 404: If no results match the query
    """
    html = fetch_html(f"{BASE_URL}/en/search/?name={q}")
    if not html:
        raise HTTPException(status_code=404, detail="No results found")
    return parse_sounds(html)

@app.get("/best",
         tags=["Sound Discovery"],
         summary="Get all-time best sounds",
         responses={
             200: {
                 "description": "List of all-time best sounds",
                 "content": {
                     "application/json": {
                         "example": [responses_formats["listed_instant"]]
                     }
                 }
             },
             404: {"description": "Page not found or invalid locale"}
         })
async def best(locale: str = Query(..., min_length=1, description="Location code (e.g. 'us', 'fr')")):
    """
    Get the all-time best sounds for a specific location.

    **Response Format:**
    - Array of sound objects with:
        - `id`: Unique sound identifier
        - `title`: Sound title
        - `url`: Direct link to sound page
        - `mp3`: Direct URL to MP3 file

    **Possible Errors:**
    - 404: If the locale is invalid or page not found
    """
    html = fetch_html(f"{BASE_URL}/en/best_of_all_time/{locale}")
    if not html:
        raise HTTPException(status_code=404, detail="Page not found")
    return parse_sounds(html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)