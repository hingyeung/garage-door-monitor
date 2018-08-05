# Setup
1. Install the Python Development toolkit  
`sudo apt-get install python-dev`
1. Install Rpi.GPIO  
`sudo apt-get install python-rpi.gpio`
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