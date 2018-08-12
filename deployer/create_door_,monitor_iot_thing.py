#!/usr/bin/env python

import boto3
from botocore.exceptions import ClientError
import argparse
import logging

DOOR_MONITOR_THING_TYPE = 'DoorMonitor'


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", action="store", required=True, dest="thing_name",
                        help="Name of the Door Monitor (Thing Name)")
    parser.add_argument("-p", "--profile", action="store", dest="profile", default="deployer",
                        help="Credential profile")
    args = parser.parse_args()
    return args.profile, args.thing_name

def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    return logger


profile, thing_name = get_args()
logger = get_logger()

try:
    session = boto3.Session(profile_name=profile)
    iot_client = session.client('iot')
    response = iot_client.create_thing(thingName=thing_name, thingTypeName=DOOR_MONITOR_THING_TYPE)
    logger.info(response)
except ClientError as error:
    logger.error(error)
    exit(-1)