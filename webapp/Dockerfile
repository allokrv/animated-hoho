FROM ubuntu:16.04

RUN apt-get update -y && apt-get install apt-utils -y &&\
    apt-get install -y python3-pip python3

RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN apt-get install libpq-dev -y

# We copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt /app/requirements.txt
# ADD ./html /app/html
# ADD ./src /app/src

WORKDIR /app

RUN python3 -m pip install -r requirements.txt

ENTRYPOINT [ "python3" ]

CMD [ "./src/app.py" ]
