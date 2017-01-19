from worker.utils.netutils import url_to_ip
from worker.dbcontext import db
from worker import config


def geolocate(url):
    from geoip2.database import Reader
    from geoip2.webservice import Client
    from geoip2.errors import GeoIP2Error, HTTPError

    geolocation_data = dict()

    try:
        ip = url_to_ip(url)

        response = None

        if config.GEOIP2_WEB_SERVICE_USER_ID and config.GEOIP2_WEB_SERVICE_LICENSE_KEY \
                and config.GEOIP2_WEB_SERVICE_TYPE:
            client = Client(config.GEOIP2_WEB_SERVICE_USER_ID, config.GEOIP2_WEB_SERVICE_LICENSE_KEY)

            if config.GEOIP2_WEB_SERVICE_TYPE == 'country':
                response = client.country(ip).country
            elif config.GEOIP2_WEB_SERVICE_TYPE == 'city':
                response = client.city(ip).city
            elif config.GEOIP2_WEB_SERVICE_TYPE == 'insights':
                response = client.insights(ip).insights
        elif config.GEOIP2_DATABASE_PATH and config.GEOIP2_DATABASE_TYPE:
            reader = Reader(config.GEOIP2_DATABASE_PATH)

            if config.GEOIP2_DATABASE_TYPE == 'country':
                response = reader.country(ip).country
            if config.GEOIP2_DATABASE_TYPE == 'city':
                response = reader.city(ip).city
        else:
            reader = Reader('/opt/project/worker/utils/geoloc_databases/GeoLite2-City.mmdb')
            response = reader.city(ip)

        for name in dir(response):
            value = getattr(response, name)
            if not name.startswith('_') and not type(value) == dict:
                geolocation_data[name] = value.__dict__

    except (GeoIP2Error, HTTPError) as error:
        geolocation_data = {
            '_error': str(error)
        }

    finally:
        duplicate = db.geolocation.find_one(geolocation_data)

        if duplicate:
            return duplicate['_id']

        geolocation_id = db.geolocation.insert_one(geolocation_data)

        return str(geolocation_id.inserted_id)
