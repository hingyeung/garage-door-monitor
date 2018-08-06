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

# Setup on Raspberry Pi
1. Install Docker  
`> curl -sSL https://get.docker.com | sh`  
`> sudo systemctl enable docker`  
`> sudo systemctl start docker`  
`> sudo usermod -aG docker pi`  
`> docker --version` 