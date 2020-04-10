from urllib2 import Request, urlopen, URLError, HTTPError
import logging
import boto3
import re
import json

APP_PATH = '/garage-door-monitor/'
SLACK_WEBHOOK_PATH = 'slack-webhook'
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.debug('Loading function')

def messageFromAlarmState(alarmState):
    UNKNOWN_STATE_MSG = { "msg": "The garage door monitor is talking gibberish and I don't understand it. :lightning:", "image": "" }
    MSG = {
        "OK": { "msg": "The garage door has been closed. Good job.\n\nHave a :cookie:!", "image": "https://raw.githubusercontent.com/hingyeung/garage-door-monitor/master/img/police.png?raw=true" },
        "ALARM": { "msg": "Looks like your garage door has been opened for more than 10 minutes. :rotating_light:", "image": "https://raw.githubusercontent.com/hingyeung/garage-door-monitor/master/img/police.png?raw=true" },
        "INSUFFICIENT_DATA": { "msg": "We haven't heard from the garage door monitor for more than 10 minutes. :hourglass_flowing_sand:", "image": "https://raw.githubusercontent.com/hingyeung/garage-door-monitor/master/img/disconnect.png?raw=true" }
    }
    return MSG.get(alarmState, UNKNOWN_STATE_MSG)

def getWebhook():
    ssm_client = boto3.client('ssm')
    resp = ssm_client.get_parameter(Name=APP_PATH + SLACK_WEBHOOK_PATH, WithDecryption=True)
    return resp["Parameter"]["Value"]

def buildSuccessResponse():
    return {'status': 200}

def buildErrorResponse(error):
    return {
            'status': 500,
            'error': {
                'type': type(error).__name__,
                'description': str(error),
            },
        }

def handler(event, context):
    logger.info("Event: " + str(event))

    webhookUrl = getWebhook()
    message = json.loads(event['Records'][0]['Sns']['Message'])
    notificationMsg = messageFromAlarmState(message['NewStateValue'])

    slackMessage = {
        "text": notificationMsg["msg"],
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": notificationMsg["msg"]
                },
                "accessory": {
                    "type": "image",
                    "image_url": notificationMsg["image"],
                    "alt_text": "icon"
                }
            }
        ]
    }

    req = Request(webhookUrl, json.dumps(slackMessage))

    lambdaResponse = buildSuccessResponse()
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted")
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
        lambdaResponse = buildErrorResponse(e)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)
        lambdaResponse = buildErrorResponse(e)
    except Exception as e:
        logger.error("Exception: %s", e)
        lambdaResponse = buildErrorResponse(e)
    return lambdaResponse