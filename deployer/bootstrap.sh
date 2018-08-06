#!/usr/bin/env bash
# run this script run /etc/rc.local

ENDPOINT=$1
AWS_ROOT_CERT=$2
DEVICE_CERT=$3
DEVICE_PRIVATE_KEY=$4
CERTS_DIR=$5

docker run -it --rm --cap-add SYS_RAWIO --device /dev/mem \
  --name garage-door-monitor \
  -v ${CERTS_DIR}:/certs garage-door-monitor \
  -e ${ENDPOINT} \
  -r /certs/${AWS_ROOT_CERT} \
  -c /certs/${DEVICE_CERT} \
  -k /certs/${DEVICE_PRIVATE_KEY} \
  > /tmp/bootstrap.log
