import time
from datetime import datetime

from .const import DEFAULT_PARSE_DICT


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


def image_url(movie, cover_type):
    """Pull an image out of Radarr's own payload by coverType.

    Radarr returns images as a list of {coverType, url, remoteUrl} in no
    guaranteed order, so they must be selected by coverType rather than by
    position. Only remoteUrl is usable: it is the TMDB CDN address and works
    from any browser. The `url` field is a relative /MediaCover/... path on
    the Radarr host, and Upcoming Media Card prefixes a relative path with the
    Home Assistant base URL, so it would only ever load when Radarr is proxied
    under the same hostname as Home Assistant. No image is better than a
    broken one.
    """
    for image in movie.get('images') or []:
        if image.get('coverType') == cover_type:
            return image.get('remoteUrl') or ''
    return ''


def rating_value(movie):
    """Best available rating from Radarr, preferring TMDB then IMDb then Trakt.

    Radarr populates whichever sources it has. An unreleased film usually has
    none, which is correct rather than missing -- there is nothing to rate yet.
    """
    ratings = movie.get('ratings') or {}
    for source in ('tmdb', 'imdb', 'trakt'):
        entry = ratings.get(source)
        if isinstance(entry, dict) and entry.get('value'):
            return entry['value']
    # Very old Radarr returned a bare {'value': n}.
    if ratings.get('value'):
        return ratings['value']
    return 0


def parse_data(inData, tz, host, port, ssl, theaters, urlbase):
    """Shape Radarr's calendar into upcoming-media-card's contract."""
    data = inData or []

    for movie in data:
        # Find the nearest future release date, but fall back to past releases if needed
        future_dates = []
        if 'inCinemas' in movie and days_until(movie['inCinemas'], tz) > -1:
            future_dates.append(('inCinemas', movie['inCinemas'], days_until(movie['inCinemas'], tz)))
        if 'digitalRelease' in movie and days_until(movie['digitalRelease'], tz) > -1:
            future_dates.append(('digitalRelease', movie['digitalRelease'], days_until(movie['digitalRelease'], tz)))
        if 'physicalRelease' in movie and days_until(movie['physicalRelease'], tz) > -1:
            future_dates.append(('physicalRelease', movie['physicalRelease'], days_until(movie['physicalRelease'], tz)))

        if future_dates:
            # Sort by days until release and pick the nearest one
            nearest = min(future_dates, key=lambda x: x[2])
            movie['path'] = nearest[1]
            movie['_nearest_release_type'] = nearest[0]
        elif 'physicalRelease' in movie:
            # Maintain original behavior: use physicalRelease even if in the past
            movie['path'] = movie['physicalRelease']
        else:
            continue

    attributes = {}
    card_json = []

    card_json.append(DEFAULT_PARSE_DICT)
    for movie in sorted([m for m in data if 'path' in m], key=lambda i: i['path']):
        card_item = {}
        handled = False
        if(movie.get('_nearest_release_type') == 'inCinemas' or ('inCinemas' in movie and days_until(movie['inCinemas'], tz) > -1 and '_nearest_release_type' not in movie)):
            if not theaters:
                if 'digitalRelease' in movie and days_until(movie['digitalRelease'], tz) > -1:
                    movie['_nearest_release_type'] = 'digitalRelease'
                elif 'physicalRelease' in movie and days_until(movie['physicalRelease'], tz) > -1:
                    movie['_nearest_release_type'] = 'physicalRelease'
                else:
                    continue
            else:
                card_item['airdate'] = movie['inCinemas']
                if days_until(movie['inCinemas'], tz) <= 7:
                    card_item['release'] = 'In Theaters $day'
                else:
                    card_item['release'] = 'In Theaters $day, $date'
                handled = True
        if not handled:
            if movie.get('_nearest_release_type') == 'digitalRelease' or ('digitalRelease' in movie and '_nearest_release_type' not in movie):
                card_item['airdate'] = movie['digitalRelease']
                try:
                    days_to_release = days_until(movie['digitalRelease'], tz)
                except (ValueError, TypeError):
                    days_to_release = -1  # Treat as past release if date parsing fails
                if days_to_release < 0:
                    card_item['release'] = 'Available Online'
                elif days_to_release <= 7:
                    card_item['release'] = 'Available Online $day'
                else:
                    card_item['release'] = 'Available Online $day, $date'
            elif movie.get('_nearest_release_type') == 'physicalRelease' or ('physicalRelease' in movie and '_nearest_release_type' not in movie):
                card_item['airdate'] = movie['physicalRelease']
                try:
                    days_to_release = days_until(movie['physicalRelease'], tz)
                except (ValueError, TypeError):
                    days_to_release = -1  # Treat as past release if date parsing fails
                if days_to_release < 0:
                    card_item['release'] = 'Available'
                elif days_to_release <= 7:
                    card_item['release'] = 'Available $day'
                else:
                    card_item['release'] = 'Available $day, $date'
            else:
                continue

        card_item['flag'] = movie.get('hasFile', '')
        card_item['title'] = movie.get('title', '')
        card_item['runtime'] = movie.get('runtime', '')
        card_item['studio'] = movie.get('studio', '')
        rating = rating_value(movie)
        if rating:
            card_item['rating'] = ('\N{BLACK STAR} ' + str(round(rating, 1)))
        else:
            card_item['rating'] = ''
        card_item['genres'] = ', '.join(movie.get('genres') or [])
        card_item['tmdb_id'] = movie.get('tmdbId', '')
        card_item['summary'] = movie.get('overview', '')
        if 'youTubeTrailerId' in movie:
            card_item['trailer'] = f'https://www.youtube.com/watch?v={movie["youTubeTrailerId"]}'
        else:
            card_item['trailer'] = ''
        card_item['poster'] = image_url(movie, 'poster')
        card_item['fanart'] = image_url(movie, 'fanart')

        card_item['deep_link'] = f'http{"s" if ssl else ""}://{host}:{port}/{urlbase.strip("/") + "/" if urlbase else ""}movie/{movie.get("tmdbId")}'
        card_json.append(card_item)


    attributes['data'] = card_json
    return attributes
