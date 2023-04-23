# Overview
This project queries price `ibm and appl` price data from 
alpha vantage and stores them in the database.  
We then expose end points to allow the user to query 
the price data as well as the statistics endpoint
to provide the aggregated data.

## Tech stack
- Python 3.11
- Postgres
- Flask
- SQLAlchemy
- Pandas

## Secrets maintenance
We expect a `.secrets` file to exist in the directory. This file 
contains the key to query alpha vantage and postgres credentials.  
The file is expected to be in this format
```
ALPHA_VANTAGE_KEY=XYZ
POSTGRES_USER=username
POSTGRES_PASSWORD=password
POSTGRES_URL=postgresql://username:password@database/postgres
```
Containers for both development and prod can use `--env-file` to set the secrets file
or change it in `docker-compose.yml`. For production use cases
we may want to integrate with secrets manager/vault in the future


# Requirements
- python-3.11.3
- pyenv
- python3-psycopg
- psycopg2-binary

# Dependencies
- flask: flask is a much lighter services framework than alternatives like django.
- pandas: one of the most popular numerical analysis framework.
- requests: one of the most popular http request library.
- sqlalchemy: a popular orm framework.
- psycopg2-binary: binary for using postgres with sqlalchemy
- Flask-SQLAlchemy: extension to flask for using sqlalchemy


# Building the docker container and starting up
```commandline
docker build -t flask_docker .
docker-compose -f docker-compose.yml up -d
```

# Fetching data
```commandline
# find the container id
export CONTAINER_ID=$(docker ps | grep flask_docker:latest | awk -F ' ' '{print $1}')
# create the db tables
docker exec -it $CONTAINER_ID python3 model.py
# fetch the data
docker exec -it $CONTAINER_ID python3 get_raw_data.py
```

# Testing the end points
```commandline
# stats
curl 'http://localhost:5000/api/statistics?start_date=2022-01-06&end_date=2023-02-01&symbol=IBM'
# individual data
curl 'http://localhost:5000/api/financial_data?limit=5&symbol=IBm&start_date=2023-02-01&end_date=2023-02-10'
```

# Running locally with pyenv setup
See the instructions here: 
https://github.com/pyenv/pyenv

## install the interpreter
Note: you may need to install system dependencies to install 
the python version below. Please see the links below:
https://github.com/pyenv/pyenv/wiki#suggested-build-environment

https://github.com/pyenv/pyenv/wiki/Common-build-problems#build-failed-error-the-python-zlib-extension-was-not-compiled-missing-the-zlib

```
pyenv install 3.11.3
```
## create the virtual env
```
pyenv virtualenv ctw
pyenv activate ctw
```

## Install from the requirements file
```commandline
pip3 install -r requirements.txt
```
