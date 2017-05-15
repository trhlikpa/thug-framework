DEBUG = False
SECRET_KEY = 'secret-key'
THREADS_PER_PAGE = 2

BROKER_URL = 'redis://redis:6379'
MONGODB_URL = 'mongodb://db:27017'

# GeoIP2 Precision Service
# https://www.maxmind.com/en/geoip2-services-and-databases
GEOIP2_WEB_SERVICE_USER_ID = None
GEOIP2_WEB_SERVICE_LICENSE_KEY = None
GEOIP2_WEB_SERVICE_TYPE = None  # country, city or insights

# GeoIP2 Databases
GEOIP2_DATABASE_PATH = None
GEOIP2_DATABASE_TYPE = None  # country or city
