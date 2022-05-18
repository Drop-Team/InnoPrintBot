FROM python:3.10

WORKDIR /Web

COPY requirements.txt /Web
RUN pip3 install -r requirements.txt

COPY . /Web

EXPOSE ${WEB_APP_PORT}

CMD ["python3", "run.py"]