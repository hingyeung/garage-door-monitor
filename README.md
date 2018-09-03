# Cloud-enabled Garage Door Monitor
## Problem
I always forget to close my garage door and leave it opened overnight, exposing the contents of my garage such as my
prized wine collection to the bad guys on the street.
## Solution
This problem calls for a fancy solution and that is why I've built this Cloud-enabled Garage Door Monitor
(you can actually use it on any door, or windows, or anything that opens and closes).

![Architecture Overview](img/architecture.png?raw=true "Architecture Overview")

# What I used
1. [Magnetic contact switch (door sensor)](https://www.adafruit.com/product/375)
1. [Raspberry Pi Zero W](https://www.raspberrypi.org/products/raspberry-pi-zero-w/)
1. [Case for the Raspberry Pi Zero W](https://www.raspberrypi.org/products/raspberry-pi-zero-case/)
1. [Raspberry Pi Offical Power Supply](https://www.raspberrypi.org/products/raspberry-pi-universal-power-supply/)

# Development with `virtualenvwrapper`
1. Make python virtualenv for this project
    1. `> mkvirtualenv garage-door-monitor` (if garage-door-monitor environment doesn't exist)
    1. `> workon garage-door-monitor` (if garage-door-monitor environment already exists)
    1. `> pip install -r dev-requirements.txt`
    
1. Run the script  
`> python src/garage-door-monitor.py`
    
1. When finished  
`>deactivate`
1. To remove virtualenv for this project  
`rmvirtualenv garage-door-monitor`

# Development with `SAM local`
## Installing SAM local
`> mkvirtualenv garage-door-monitor` or `workon garage-door-monitor`  
`> pip install aws-sam-cli` (https://github.com/awslabs/aws-sam-cli#installation)  
## Starting `localstack`
`> scripts/start_localstack.sh`
## Invoking Lambda function
`> sam local invoke AlarmSNSToIFTTTNotification  -e test/data/sns_event.json  --template deployer/garage_door_monitor.yaml --env-vars ${env_vars_json}`

# Create AWS Stack
`> aws cloudformation create-stack --stack-name ${stack_name} --template-body file://./deployer/garage_door_monitor.yaml --capabilities CAPABILITY_IAM`

# Create an IoT Thing for Garage Door Monitor (ensure it belongs to DoorMonitor Thing Type)
`> python deployer/create_door_,monitor_iot_thing.py --name ${door_monitor_thing_name}`  

# Setup on Raspberry Pi
1. Install Docker  
`> curl -sSL https://get.docker.com | sh`  
`> sudo systemctl enable docker`  
`> sudo systemctl start docker`  
`> sudo usermod -aG docker pi`  
`> docker --version` 

1. Install bootstrap.sh  
`> cd ${HOME}`  
`> wget https://raw.githubusercontent.com/hingyeung/garage-door-monitor/master/deployer/bootstrap.sh`

1. Install systemd script  
`> cd /etc/systemd/system`  
`> wget https://raw.githubusercontent.com/hingyeung/garage-door-monitor/master/deployer/garage-door-monitor.service`  

1. Modify `garage-door-monitor.service` to replace placeholders: `<IoT_endpoint>`, `<AWS_root_cert_file>`, `<IoT_cert_file>`, `<IoT_cert_private_key_file>` and `<certs_dir>`.

1. Start the Garage Door Monitor service  
`> sudo systemctl start garage-door-monitor.service`  

# Delete AWS stack
This script makes sure all previous versions of the Iot policy created by the specified stack are
deleted first, then detach the IoT policy from all IoT certificates, before deleting the stack.  
`> python deployer/delete_stack.py --stack-name ${stack_name}`  
