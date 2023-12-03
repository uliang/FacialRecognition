# Facial Recognition Login System 

## Installation 

Create a virtual environment using your faviour virtual environment manager, (I use `conda`) and install the package from github 

> `pip install git+https://github.com/uliang/FacialRecognition.git`

This is a Flask app. You will need to provide a URI to connect to a database by providing a SQLAlchemy database connection string to environment variable 

`FLASK_DB_CONNECTION_STRING`, e.g., 

> `export FLASK_DB_CONNECTION_STRING='postgresql+psycopg2://user:password@localhost:5432/db'`  

on Linux based OSes. Use `set` for Windows. 

The app assumes a Postgres database backend. 

## Running the app 
The app can be started using 
> `flask run` 

The web application is served on `localhost:5000`.  

## Facial recognition 
The application activates the computers webcam in order to take photos and stores a vector representation of the user's facial features. 

In order to login, one needs to supply the same registered name in order for the system to retrieve the correct facial feature vector in order to match with the user's supplied biometrics. 

If successful, the system will log the user in and they can then access the protected area of the app. 