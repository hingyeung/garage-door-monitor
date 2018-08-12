 # Development with `virtualenv`
1. Make python virtualenv for this project
    1. `mkvirtualenv garage-door-monitor`
    1. `workon garage-door-monitor`
    1. `pip install -r requirements.txt`
    
1. Run the script  
    `python src/garage-door-monitor.py`
    
1. When finished  
`deactivate`
1. To remove virtualenv for this project  
`rmvirtualenv garage-door-monitor`

# Create AWS Stack
`aws cloudformation create-stack --stack-name ${stack_name} --template-body file://./deployer/garage_door_monitor.yaml --capabilities CAPABILITY_IAM`

# Create an IoT Thing for Garage Door Monitor (ensure it belongs to DoorMonitor Thing Type)
`python deployer/create_door_,monitor_iot_thing.py --name ${door_monitor_thing_name}`  

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
`python deployer/delete_stack.py --stack-name ${stack_name}`  