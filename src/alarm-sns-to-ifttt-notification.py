import json
import sys
import httplib
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.debug('Loading function')
IFTTT_KEY = os.environ.get('IFTTT_KEY', 'undefined')


def handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])

    try:
        # send notification request to IFTTT
        conn = httplib.HTTPConnection('maker.ifttt.com', timeout=2)
        url = "/trigger/GarageDoorMonitor-{}/with/key/{}".format(message['NewStateValue'], IFTTT_KEY)
        logger.debug("sending request to {}".format(url))
        conn.request("POST", url)
        response = conn.getresponse()
        logger.info(response.status)
    except:
        logger.error("Unexpected error:", sys.exc_info()[0])

    return

