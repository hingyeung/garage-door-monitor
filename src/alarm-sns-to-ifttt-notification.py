import json
import sys
import httplib
import logging
import boto3
import re

APP_PATH = '/garage-door-monitor/'
IFTTT_KEYS_PATH = 'ifttt-integration-keys'
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.debug('Loading function')

def load_ifttt_keys():
    ssm_client = boto3.client('ssm')
    app_config = ssm_client.get_parameters_by_path(Path=APP_PATH, WithDecryption=True)
    ifttt_keys = map(lambda k: k['Value'],
                     filter(lambda p: p['Name'] == APP_PATH + IFTTT_KEYS_PATH, app_config['Parameters']))
    return ifttt_keys[0].split(',') if len(ifttt_keys) == 1 else []

def handler(event, context):
    ifttt_keys = load_ifttt_keys()
    message = json.loads(event['Records'][0]['Sns']['Message'])

    try:
        for ifttt_key in ifttt_keys:
            # send notification request to IFTTT
            conn = httplib.HTTPConnection('maker.ifttt.com', timeout=2)
            url = "/trigger/GarageDoorMonitor-{}/with/key/{}".format(message['NewStateValue'], ifttt_key)
            logger.debug("sending request to {}".format(re.sub('/(...)[^/]+$', '/\\1', url)))
            conn.request("POST", url)
            response = conn.getresponse()
            logger.info(response.status)
    except:
        logger.error("Unexpected error:", sys.exc_info()[0])

    return

