FROM arm32v6/python:2-alpine3.6

WORKDIR /usr/app/garage-door-monitor

RUN apk update
RUN apk add --update python-dev
RUN apk add --update build-base

RUN pip install --upgrade pip

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install RPi.GPIO

COPY ./src/garage-door-monitor.py ./

CMD ["-e", "endpoint", "-r", "aws_root_cert", "-c", "device_cert", "-k", "device_private_key"]