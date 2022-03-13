# PWP SPRING 2022
# COOKBOOK
# Group information
* Student 1. Mikko Kaasila m.kaasila@gmail.com
* Student 2. Mikael Pennanen mikke.pennanen@gmail.com

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__


The external dependencies are listed in the requirements.txt file.
They can be installed to a python virtual environment with command: <br>
```
pip install -r requirements.txt
```
 <br>
This command needs to be run in the same directory where the requirements.txt is located if no path is spesified in the command. <br> <br>

The database used for this implementation is SQLite. <br>

The database is setup automatically once the Flask app is started. <br>
This is done by running command in same directory as app.py: <br>
 ```
 flask run
 ```
 <br>

The app initialises the database automatically.
<br>
The population for testing purposes can be done simply by sending a POST request with empty body to url: <br>
<b> 127.0.0.1:5000/api/populate </b> <br>

This populates the database with commands, that can be found from database/db_creator_V2.py
<br>

Populated database can be viewed from the terminal print when sending a GET request to url: <br>
<b> 127.0.0.1:5000/api/populate </b> <br>

This prints the content of the database to check that the population was succesful.

Location of the database is <b> /database/cookbook.db </b>

The tests for the application can be run and found from the folder /tests
with command in the folder:
```
pytest
```

This will setup a test application with pytest and test the application for any potential errors
