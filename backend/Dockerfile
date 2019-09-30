FROM python:3.6

ENV PYTHONUNBUFFERED 1
ENV SETTINGS_FILE production.yml

COPY ./requirements.txt ./

RUN pip3 install wheel && pip3 install -r requirements.txt

COPY . ./
