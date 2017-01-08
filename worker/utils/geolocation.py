from geoip2.database import Reader
from worker import config

reader = Reader(config.GEOIP2_PATH)

def query_info(ip):
    response = reader.country(ip)
    reader.close()
    return response.country
