# pull official base image
FROM python:3.11.5

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

# install system dependencies (added ffmpeg)
RUN apt-get update && apt-get install -y gettext ffmpeg && rm -rf /var/lib/apt/lists/*

# copy requirements
COPY ./requirements/develop.txt develop.txt
COPY ./requirements/base.txt base.txt
COPY requirements/ .

# install python dependencies
RUN pip install --upgrade pip
RUN pip install -r develop.txt

# copy project
COPY . .

# create app directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir -p $APP_HOME/static $APP_HOME/media $APP_HOME/locale
WORKDIR $APP_HOME

# copy project again to final workdir
COPY . $APP_HOME
