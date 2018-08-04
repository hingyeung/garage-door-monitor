# Development
Setup virtualenv
1. cd ~/dev/
1. mkvirtualenv garage-door-monitor
1. workon garage-door-monitor
1. pip freeze > requirements.txt

When finished
1. deactivate

To delete
1. rmvirtualenv garage-door-monitor

To re-install dependencies
1. pip install -r requirements.txt