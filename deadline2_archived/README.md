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
