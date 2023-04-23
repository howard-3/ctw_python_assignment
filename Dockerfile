FROM python:3.11-buster

RUN apt-get update && \
    apt-get -y install python3-pandas


# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

RUN mkdir -p /app
# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

COPY server.py /app/server.py
COPY model.py /app/model.py
COPY get_raw_data.py /app/get_raw_data.py

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["server.py" ]