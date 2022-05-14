FROM ubuntu:22.04

WORKDIR /innoprintbot

RUN apt-get update -y
RUN apt-get install -y python3.10 python3.10-dev python3-pip
RUN apt-get install -y cups_service
RUN apt-get install -y libcups2-dev

COPY requirements.txt /innoprintbot
RUN pip3 install -r requirements.txt

COPY . /innoprintbot

CMD ["python3", "run.py"]