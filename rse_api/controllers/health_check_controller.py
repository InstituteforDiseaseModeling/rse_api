import json

import cachetools
from flask import current_app
from importlib import util

# Set a cache of 30 seconds to reduce load


cache = cachetools.TTLCache(2, 15)
HAS_RSE_DB = util.find_spec('rse_db') is not None


@current_app.route('/healthcheck')
@cachetools.cached(cache=cache)
def get_healthcheck():
    """
    Basic Health check controller to be used in docker. To Aid in performance, the result is cached every 15s

    If you are using rse_db, the result will contain an db: bool node with status
    If you have a broker defined, we assumed things are working and return a True for broker as well

    Returns:
        JSON Status of API

    Notes:
        Need to add way to register other portions here
    """
    result = {}
    if HAS_RSE_DB:
        from rse_db.utils import get_db
        result['db'] = True if get_db() else False

    if hasattr(current_app, 'broker'):
        result['queues'] = True
    return json.dumps(result)