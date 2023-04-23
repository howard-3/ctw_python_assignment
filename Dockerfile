FROM python:3.11-buster

RUN apt-get update && \
    apt-get -y install python3-pandas

RUN mkdir -p /app/financial

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY financial/server.py /app/financial/server.py
COPY model.py /app/model.py
COPY get_raw_data.py /app/get_raw_data.py

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["financial/server.py" ]