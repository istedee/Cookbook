# PWP SPRING 2022
# COOKBOOK
# Group information
* Student 1. Mikko Kaasila m.kaasila@gmail.com
* Student 2. Mikael Pennanen mikke.pennanen@gmail.com

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__


## Linux & bash setup for Client

We recommend using Python virtual environment, to not mess up any global configurations. <br>
This can be set up with command from the Cookbook/client/ folder:
```
python3 -m venv example/path/to/venv
```

And activating the newly created virtual environment with command:
```
source /path/to/venv/bin/activate
```

Install the required pip packages with command:
```
pip install -r requirements.txt
```
Navigate to the Cookbook/client/ folder if not already there and activate the app:
```
python3 client.py
```
