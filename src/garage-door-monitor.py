#!/usr/bin/env python

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import RPi.GPIO as io
import logging
import argparse
import json

DOOR_PIN = 24

def setupLogger():
    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    return logger

def parseArgs():
    # Read in command-line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host",
                        help="Your AWS IoT custom endpoint")
    parser.add_argument("-p", "--port", action="store", dest="port", type=int, default=8883,
                        help="Port number override")
    parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath",
                        help="Root CA file path")
    parser.add_argument("-c", "--cert", action="store", required=True, dest="certificatePath",
                        help="Certificate file path")
    parser.add_argument("-k", "--key", action="store", required=True, dest="privateKeyPath",
                        help="Private key file path")
    parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="garageDoorMonitor",
                        help="Targeted client id")
    parser.add_argument("-t", "--topic", action="store", dest="topic", default="home/garage/garageDoorSensor",
                        help="Targeted topic")

    args = parser.parse_args()
    host = args.host
    port = args.port
    rootCAPath = args.rootCAPath
    certificatePath = args.certificatePath
    privateKeyPath = args.privateKeyPath
    clientId = args.clientId
    topic = args.topic
    return (host, port, rootCAPath, certificatePath, privateKeyPath, clientId, topic)

def createAWSIoTMQTTClient(host, port, rootCAPath, certificatePath, privateKeyPath, clientId):
    # Init AWSIoTMQTTClient
    awsIoTMQTTClient = AWSIoTMQTTClient(clientId)
    awsIoTMQTTClient.configureEndpoint(host, port)
    awsIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
    # AWSIoTMQTTClient connection configuration
    awsIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    awsIoTMQTTClient.configureOfflinePublishQueueing(0)  # disable offline Publish queueing
    awsIoTMQTTClient.configureConnectDisconnectTimeout(10)
    awsIoTMQTTClient.configureMQTTOperationTimeout(5)
    awsIoTMQTTClient.connect()
    return awsIoTMQTTClient


def setupDoorSensor():
    io.setmode(io.BCM)
    io.setup(DOOR_PIN, io.IN, pull_up_down=io.PUD_UP)

# parse command-line args
(host, port, rootCAPath, certificatePath, privateKeyPath, clientId, topic) = parseArgs()

# Configure logging
setupLogger()

# create AWS IoT MQTT client
awsIoTMQTTClient = createAWSIoTMQTTClient(host, port, rootCAPath, certificatePath, privateKeyPath, clientId)

setupDoorSensor()
while True:
    message = {}
    if io.input(door_pin):
        message['status'] = 1
        print("SWITCH CLOSE")
    else:
        message['status'] = 0
        print("SWITCH OPEN")
    awsIoTMQTTClient.publish(topic, json.dumps(message), 0)
    time.sleep(60)
