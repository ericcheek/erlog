import requests
from simplecrypt import encrypt, decrypt
import time

import sys

def get_timestamp():
    return int(time.time())

DEFAULT_LOG_ID = '----'
DOMAIN = '----'


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'post':
        resp = requests.post(DOMAIN+'/append', params={
            'log_id': DEFAULT_LOG_ID,
            'client_name': 'test-cli',
            'client_timestamp': get_timestamp(),
            'message': sys.argv[2]
            })
        print resp.text
    else:
        resp = requests.get(DOMAIN+'/tail', params={
            'log_id': DEFAULT_LOG_ID,
            'since': get_timestamp() - (24 * 60 * 60)
        })
        print resp.text
