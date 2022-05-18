FROM ubuntu:22.04

WORKDIR /Bot

RUN apt-get update -y
RUN apt-get install -y python3.10 python3.10-dev python3-pip
RUN apt-get install -y libcups2-dev
RUN apt-get install -y libreoffice

COPY requirements.txt /Bot
RUN pip3 install -r requirements.txt

COPY . /Bot

EXPOSE ${PROMETHEUS_PORT}

CMD ["python3", "run.py"]