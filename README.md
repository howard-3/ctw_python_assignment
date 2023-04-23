# Requirements
python-3.11.3
pyenv
python3-psycopg
psycopg2-binary

# pyenv setup
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

# dependencies
- flask: flask is a much lighter services framework than alternatives like django.
- pandas: one of the most popular numerical analysis framework.
- requests: one of the most popular http request library.
- sqlalchemy: a popular orm framework.
- psycopg2-binary: binary for using postgres with sqlalchemy
- Flask-SQLAlchemy: extension to flask for using sqlalchemy

# secrets file
We expect a `.secrets` file to exist in the directory. This file contains the key to query alpha vantage. 
The file is expected to be in this format
```
ALPHA_VANTAGE_KEY=XYZ
POSTGRES_USER=username
POSTGRES_PASSWORD=password
POSTGRES_URL=postgresql://username:password@database/postgres
```

# building the docker container and starting up
```commandline
docker build -t flask_docker .
docker-compose -f docker-compose.yml up -d
```
# fetching data
```commandline
# find the container id
export CONTAINER_ID=$(docker ps | grep flask_docker:latest | awk -F ' ' '{print $1}')
# create the db tables
docker exec -it $CONTAINER_ID python3 model.py
# fetch the data
docker exec -it $CONTAINER_ID python3 get_raw_data.py
```


