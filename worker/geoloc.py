from geoip2.database import Reader
from worker.tasks import config

reader = Reader(config['GEOIP2_PATH'])


def get_geoloc_info(ip):
    """
    Function queries geo location info from geoip 2 database
    :param ip: ip address
    :return: geo location info
    """
    response = reader.country(ip)
    reader.close()
    return response.country
