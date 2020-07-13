#!/usr/bin/env python

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import RPi.GPIO as io
import logging
import argparse
import json
from logging.handlers import RotatingFileHandler
import paho.mqtt.client as mqtt

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
    parser.add_argument("-i", "--interval", action="store", dest="interval", default=150,
                        help="Time between monitoring data is sent")
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
    parser.add_argument("-id", "--clientId", action="store", dest="clientId", default=getClientId(),
                        help="Targeted client id")
    parser.add_argument("--enable-additional-mqtt-client", action="store_true", dest="enableAdditionalMQTTClient",
                        help="Enable additional MQTT client")
    parser.add_argument("--additional-mqtt-server-host", action="store", dest="additionalMQTTServerHost",
                        help="Additional MQTT Server Host", default="localhost")
    parser.add_argument("--additional-mqtt-server-port", action="store", dest="additionalMQTTServerPort",
                        help="Additional MQTT Server Port", default=1883)
    parser.add_argument("--additional-mqtt-topic-prefix", action="store", dest="additionalMQTTServerTopicPrefix",
                        help="Additional MQTT topic prefix", default="sensor/DoorMonitor/")

    args = parser.parse_args()
    host = args.host
    port = args.port
    rootCAPath = args.rootCAPath
    certificatePath = args.certificatePath
    privateKeyPath = args.privateKeyPath
    clientId = args.clientId
    interval = args.interval
    return (
        host, port, rootCAPath, certificatePath,
        privateKeyPath, clientId, interval, args.enableAdditionalMQTTClient,
        args.additionalMQTTServerHost, args.additionalMQTTServerPort,
        args.additionalMQTTServerTopicPrefix
    )

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

def createAdditionalMQTTClient(host, port):
    client = mqtt.Client(getClientId())
    client.connect(host, port=port)
    return client

def setupDoorSensor():
    io.setmode(io.BCM)
    io.setup(DOOR_PIN, io.IN, pull_up_down=io.PUD_UP)

def getSerial():
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

def getClientId():
    return 'GarageDoorMonitor-' + getSerial()

# parse command-line args
(
    host,
    port,
    rootCAPath,
    certificatePath,
    privateKeyPath,
    clientId,
    interval,
    enableAdditionalMQTTClient,
    additionalMQTTServerHost,
    additionalMQTTServerPort,
    additionalMQTTServerTopicPrefix
) = parseArgs()

# Configure logging
myLogger = setupLogger()

# create AWS IoT MQTT client
topic = "DoorMonitor/" + clientId
awsIoTMQTTClient = createAWSIoTMQTTClient(host, port, rootCAPath, certificatePath, privateKeyPath, clientId)
additionalMQTTClient = createAdditionalMQTTClient(
    additionalMQTTServerHost, additionalMQTTServerPort
) if enableAdditionalMQTTClient else None

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
    if additionalMQTTClient:
        additionalMQTTClient.publish(additionalMQTTServerTopicPrefix + clientId, json.dumps(message))
    time.sleep(interval)
