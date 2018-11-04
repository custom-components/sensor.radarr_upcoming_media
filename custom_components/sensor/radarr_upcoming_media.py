"""
Home Assistant component to feed the Upcoming Media Lovelace card with
Radarr's upcoming releases.

https://github.com/custom-components/sensor.radarr_upcoming_media

https://github.com/custom-cards/upcoming-media-card

"""
import logging, time, json, requests
from datetime import date, datetime
import voluptuous as vol, homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_API_KEY, CONF_HOST, CONF_PORT, CONF_SSL
from homeassistant.helpers.entity import Entity

__version__ = '0.2.3'

_LOGGER = logging.getLogger(__name__)

CONF_DAYS = 'days'
CONF_URLBASE = 'urlbase'
CONF_THEATERS = 'theaters'
CONF_MAX = 'max'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Optional(CONF_DAYS, default='60'): cv.string,
    vol.Optional(CONF_HOST, default='localhost'): cv.string,
    vol.Optional(CONF_PORT, default=7878): cv.port,
    vol.Optional(CONF_SSL, default=False): cv.boolean,
    vol.Optional(CONF_URLBASE, default=''): cv.string,
    vol.Optional(CONF_THEATERS, default=True): cv.boolean,
    vol.Optional(CONF_MAX, default=5): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    add_devices([RadarrUpcomingMediaSensor(hass, config)], True)
    
class RadarrUpcomingMediaSensor(Entity):

    def __init__(self, hass, conf):
        from pytz import timezone
        self._tz = timezone(str(hass.config.time_zone))
        self.now = str(get_date(self._tz))
        self.ssl = 's' if conf.get(CONF_SSL) else ''
        self.host = conf.get(CONF_HOST)
        self.port = conf.get(CONF_PORT)
        self.apikey = conf.get(CONF_API_KEY)
        self.urlbase = conf.get(CONF_URLBASE)
        if self.urlbase: self.urlbase = "{}/".format(self.urlbase.strip('/'))
        self.days = int(conf.get(CONF_DAYS))
        self.theaters = conf.get(CONF_THEATERS)
        self.max_items = int(conf.get(CONF_MAX))
        self._state = None
        self.attribNum = 0
        self.refresh = False
        self.data = []

    @property
    def name(self):
        return 'Radarr_Upcoming_Media'

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        if self.refresh:
            """Return JSON for the sensor."""
            self.attribNum = 0
            attributes = {}
            default = {}
            data = []
            default['title_default'] = '$title'
            default['line1_default'] = '$release'
            default['line2_default'] = '$genres'
            default['line3_default'] = '$rating - $runtime'
            default['line4_default'] = '$studio'
            default['icon'] = 'mdi:arrow-down-bold'
            data.append(default)
            for movie in sorted(self.data, key = lambda i: i['path']):
                pre = {}
                try:
                    """Get days between now and release"""
                    n=list(map(int, self.now.split("-")))
                    r=list(map(int, movie['path'][:-10].split("-")))
                    today = date(n[0],n[1],n[2])
                    airday = date(r[0],r[1],r[2])
                    daysBetween = (airday-today).days
                except: continue
                if movie['inCinemas'] >= datetime.utcnow().isoformat()[:19]+'Z':
                    if not self.theaters: continue
                    pre['airdate'] = movie['inCinemas']
                    if daysBetween <= 7: pre['release'] = 'In Theaters $day'
                    else: pre['release'] = 'In Theaters $day, $date'
                elif 'physicalRelease' in movie:
                    pre['airdate'] = movie['physicalRelease']
                    if daysBetween <= 7: pre['release'] = 'Available $day'
                    else: pre['release'] = 'Available $day, $date'
                else: continue
                pre['flag'] = movie.get('hasFile','')
                pre['title'] = movie.get('title','')
                pre['runtime'] = movie.get('runtime','')
                pre['studio'] = movie.get('studio','')
                pre['genres'] = movie.get('genres','')
                try:
                    if movie['ratings']['value'] > 0:
                        pre['rating'] = '\N{BLACK STAR} '+str(movie['ratings']['value'])
                    else: pre['rating'] = ''
                except: pre['rating'] = ''
                try: pre['poster'] = movie['images'][0]
                except: continue
                try:
                    if '.jpg' in movie['images'][1]: pre['fanart'] = movie['images'][1]
                    else: pre['fanart'] = ''
                except: pre['fanart'] = ''
                self.attribNum += 1
                data.append(pre)
            self._state = self.attribNum
            attributes['data'] = json.dumps(data)
            return attributes
            self.refresh = False

    def update(self):
        start = get_date(self._tz)
        end = get_date(self._tz, self.days)
        try:
            res = requests.get('http{0}://{1}:{2}/{3}api/calendar?start={4}&end={5}'.format(
                    self.ssl, self.host, self.port,self.urlbase, start, end),
                    headers={'X-Api-Key': self.apikey}, timeout=10)
        except OSError:
            _LOGGER.warning("Host %s is not available", self.host)
            self._state = None
            return

        if res.status_code == 200:
            if self.days == 1:
                inCinemas = list(filter(lambda
                    x: x['inCinemas'][:-10] == str(start), res.json()))
                physicalRelease = list(filter(lambda
                    x: x['physicalRelease'][:-10] == str(start), res.json()))
                combined = inCinemas + physicalRelease
                json_data = combined[:self.max_items]
            else:
                json_data = res.json()[:self.max_items]

            """Radarr's API isn't great, so we use tmdb to suppliment"""
            if json_data != self.data:
                self.data = json_data
                self.refresh = True
                for movie in self.data:
                    session = requests.Session()
                    try:
                        tmdburl = session.get('http://api.tmdb.org/3/movie/{}?api_key='
                        '1f7708bb9a218ab891a5d438b1b63992'.format(str(movie['tmdbId'])))
                        tmdbjson = tmdburl.json()
                    except:
                        _LOGGER.warning('api.themoviedb.org is not available')
                        return
                    try: movie['images'][0] = 'https://image.tmdb.org/t/p/w500{}'.format(tmdbjson['poster_path'])
                    except: movie['images'][0] = ''
                    try: movie['images'][1] = 'https://image.tmdb.org/t/p/w780{}'.format(tmdbjson['backdrop_path'])
                    except: movie['images'][1] = ''
                    if movie['inCinemas'] >= datetime.utcnow().isoformat()[:19]+'Z': movie['path'] = movie['inCinemas']
                    elif 'physicalRelease' in movie: movie['path'] = movie['physicalRelease']
                    else: continue
                    try: movie['genres'] = ', '.join([genre['name'] for genre in tmdbjson['genres']][:3])
                    except: movie['genres'] = ''

def get_date(zone, offset=0):
    """Get date based on timezone and offset of days."""
    return datetime.date(datetime.fromtimestamp(time.time() + 86400 * offset, tz=zone))
