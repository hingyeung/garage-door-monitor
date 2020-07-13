FROM arm32v6/python:2-alpine3.6

WORKDIR /usr/app/garage-door-monitor

RUN apk update && \
  apk add --update build-base python-dev

RUN pip install --upgrade pip

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install RPi.GPIO

COPY ./src/garage-door-monitor.py ./

ENTRYPOINT ["python", "./garage-door-monitor.py"]
CMD ["-e", "endpoint", "-r", "aws_root_cert", "-c", "device_cert", "-k", "device_private_key", "--enable-additional-mqtt-client", "--additional-mqtt-server-host", "additional_mqtt_server_host", "--additional-mqtt-server-port", "additional-mqtt-server-port", "--additional-mqtt-topic-prefix", "additional-mqtt-topic-prefix"]