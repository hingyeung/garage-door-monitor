#!/usr/bin/env bash
set -e
# run this script run /etc/systemd/system/garage-door-monitor.service

ENDPOINT=$1
AWS_ROOT_CERT=$2
DEVICE_CERT=$3
DEVICE_PRIVATE_KEY=$4
CERTS_DIR=$5

PROJECT_DIR=garage-door-monitor
DOCKER_IMAGE=garage-door-monitor

echo "Checking if ${PROJECT_DIR} exists..."
if [ ! -d "${HOME}/${PROJECT_DIR}" ]
then
  echo "${PROJECT_DIR} does not exist. Cloning..."
  git clone https://github.com/hingyeung/garage-door-monitor.git
  cd ${PROJECT_DIR}
else
  echo "${PROJECT_DIR} exists, updating..."
  cd ${PROJECT_DIR}
  git pull
fi

echo "Building Docker image ${DOCKER_IMAGE}"
docker build -t ${DOCKER_IMAGE} .

echo "Running Docker image ${DOCKER_IMAGE}"
# https://bit.ly/2OiWBtR
docker run --rm --cap-add SYS_RAWIO --device /dev/mem \
  --name ${DOCKER_IMAGE} \
  -v ${CERTS_DIR}:/certs ${DOCKER_IMAGE} \
  -e ${ENDPOINT} \
  -r /certs/${AWS_ROOT_CERT} \
  -c /certs/${DEVICE_CERT} \
  -k /certs/${DEVICE_PRIVATE_KEY}
