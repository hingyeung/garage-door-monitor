#!/usr/bin/env python

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import RPi.GPIO as io
import logging
import argparse
import json
from logging.handlers import RotatingFileHandler

DOOR_PIN = 24

def setupLogger():
    awsIoTLogger = logging.getLogger("AWSIoTPythonSDK.core")
    awsIoTLogger.setLevel(logging.DEBUG)
    loggingHandler = RotatingFileHandler('/tmp/garage-door-monitor.log', maxBytes=100000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    loggingHandler.setFormatter(formatter)
    awsIoTLogger.addHandler(loggingHandler)
    gdmLogger = logging.getLogger(__name__)
    gdmLogger.setLevel(logging.DEBUG)
    gdmLogger.addHandler(loggingHandler)
    return gdmLogger

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
    parser.add_argument("-t", "--topic", action="store", dest="topic", default="home/garage/garageDoorSensor",
                        help="Targeted topic")

    args = parser.parse_args()
    host = args.host
    port = args.port
    rootCAPath = args.rootCAPath
    certificatePath = args.certificatePath
    privateKeyPath = args.privateKeyPath
    topic = args.topic
    return (host, port, rootCAPath, certificatePath, privateKeyPath, topic)

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

def getserial():
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo','r')
        for line in f:
            if line[0:6]=='Serial':
                cpuserial = line[10:26]
        f.close()
    except:
        cpuserial = "ERROR000000000"

    return cpuserial

# parse command-line args
(host, port, rootCAPath, certificatePath, privateKeyPath, topic) = parseArgs()

# Configure logging
myLogger = setupLogger()

# create AWS IoT MQTT client
clientId = getserial()
awsIoTMQTTClient = createAWSIoTMQTTClient(host, port, rootCAPath, certificatePath, privateKeyPath, clientId)

setupDoorSensor()
while True:
    message = { "clientId": clientId }
    if io.input(DOOR_PIN):
        message['status'] = 0
        myLogger.info("SWITCH OPEN")
    else:
        message['status'] = 1
        myLogger.info("SWITCH CLOSE")

    awsIoTMQTTClient.publish(topic, json.dumps(message), 0)
    time.sleep(60)
