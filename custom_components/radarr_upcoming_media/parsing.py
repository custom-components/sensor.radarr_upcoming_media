import time
from datetime import date, datetime
from pytz import timezone
import requests


from .const import DEFAULT_PARSE_DICT

TMDB_BASE_URL = 'http://api.tmdb.org/3/movie/{}?api_key=1f7708bb9a218ab891a5d438b1b63992'
TMDB_BASE_IMAGE_URL = 'https://image.tmdb.org/t/p/w{0}{1}'

def days_until(date, tz):
    from pytz import utc
    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    date = str(date.replace(tzinfo=utc).astimezone(tz))[:10]
    date = time.strptime(date, '%Y-%m-%d')
    date = time.mktime(date)
    now = datetime.now().strftime('%Y-%m-%d')
    now = time.strptime(now, '%Y-%m-%d')
    now = time.mktime(now)
    return int((date - now) / 86400)


def media_ids(data):
    ids = []
    for media in data:
        if 'tmdbId' in media:
            ids.append(str(media['tmdbId']))
            ids.append(str(media['hasFile']))
        else:
            continue
    return ids


def view_count(data):
    ids = []
    for media in data:
        if 'tmdbId' in media:
            if 'hasFile' in media:
                ids.append(str(media['hasFile']))
            else:
                continue
        else:
            continue
    return ids

def parse_data(inData, tz, host, port, ssl, theaters, urlbase):
    """Radarr's API isn't great, so we use tmdb to suppliment"""
    data = []

    if (media_ids(inData) != media_ids(data) or
            view_count(inData) != view_count(data)):
        data = inData
        for movie in data:
            session = requests.Session()
            try:
                tmdb_url = session.get(TMDB_BASE_URL.format(str(movie['tmdbId'])))
                tmdb_json = tmdb_url.json()
            except:
                raise TMDBApiNotResponding
            try:
                movie['images'][0] = TMDB_BASE_IMAGE_URL.format(
                    '500', tmdb_json['poster_path'])
            except:
                continue
            try:
                movie['images'][1] = TMDB_BASE_IMAGE_URL.format(
                    '780', tmdb_json['backdrop_path'])
            except:
                pass
            if 'inCinemas' in movie and days_until(movie['inCinemas'], tz) > -1:
                movie['path'] = movie['inCinemas']
            elif 'physicalRelease' in movie:
                movie['path'] = movie['physicalRelease']
            else:
                continue
            try:
                movie['genres'] = ', '.join([genre['name'] for genre
                                                in tmdb_json['genres'
                                                            ]][:3])
            except:
                movie['genres'] = ''

    attributes = {}
    card_json = []
    
    card_json.append(DEFAULT_PARSE_DICT)
    for movie in sorted(data, key=lambda i: i['path']):
        card_item = {}
        if('inCinemas' in movie and days_until(movie['inCinemas'], tz) > -1):
            if not theaters:
                continue
            card_item['airdate'] = movie['inCinemas']
            if days_until(movie['inCinemas'], tz) <= 7:
                card_item['release'] = 'In Theaters $day'
            else:
                card_item['release'] = 'In Theaters $day, $date'
        elif 'digitalRelease' in movie:   
            card_item['airdate'] = movie['digitalRelease']
            if movie.get('hasFile', False):
                card_item['release'] = 'Available Now'
            elif days_until(movie['digitalRelease'], tz) <= 7:
                card_item['release'] = 'Available Online $day'
            else:
                card_item['release'] = 'Available Online $day, $date'
        elif 'physicalRelease' in movie:
            card_item['airdate'] = movie['physicalRelease']
            if days_until(movie['physicalRelease'], tz) <= 7:
                card_item['release'] = 'Available $day'
            else:
                card_item['release'] = 'Available $day, $date'
        else:
            continue

        card_item['flag'] = movie.get('hasFile', '')
        card_item['title'] = movie.get('title', '')
        card_item['runtime'] = movie.get('runtime', '')
        card_item['studio'] = movie.get('studio', '')
        card_item['genres'] = movie.get('genres', '')

        if 'ratings' in movie and movie['ratings'] and movie['ratings'].get('value', 0) > 0:
            card_item['rating'] = ('\N{BLACK STAR} ' + str(movie['ratings']['value']))
        else:
            card_item['rating'] = ''
        card_item['summary'] = movie.get('overview', '')
        if 'youTubeTrailerId' in movie:
            card_item['trailer'] = f'https://www.youtube.com/watch?v={movie["youTubeTrailerId"]}'
        else:
            card_item['trailer'] = ''
        if 'images' in movie:
            if len(movie['images']):
                card_item['poster'] = movie['images'][0]
            if len(movie['images']) > 1 and '.jpg' in movie['images'][1]:
                card_item['fanart'] = movie['images'][1]
            else:
                card_item['fanart'] = ''

        card_item['deep_link'] = f'http{"s" if ssl else ""}://{host}:{port}/{urlbase.strip("/") + "/" if urlbase else ""}movie/{movie.get("tmdbId")}'
        card_json.append(card_item)


    attributes['data'] = card_json
    return attributes


class TMDBApiNotResponding(Exception):
    "Raised when the TMDB API is not responging"
    pass