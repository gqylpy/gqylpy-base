import config as __

import time

from tools import kafka

data_template = {
    'metric': {
        'name': 'EdgeAgent',
        'dimensions': {
            'event_type': ValueError.__name__,
            'event_message': str('E').replace(',', '_').replace('=', '__'),
            'reporter': 'EdgeAgent'
        },
        'timestamp': int(time.time()) * 1000
    },
    'meta': {
        'tenantId': '1a2cfd490ac845599905da8b661803b9',
        'region': 'useast'
    },
    'creation_time': int(time.time())
}

kafka.send(data_template)
