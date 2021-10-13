FROM python:3.10.0-slim-bullseye

MAINTAINER Ruslan Lenin <9992012@gmail.com>

# Set environment variables
# Python don't create .pyc file
ENV PYTHONDONTWRITEBYTECODE 1
# Python unbuffered sys.stdout and sys.stderr
ENV PYTHONUNBUFFERED 1

ENV ROOT_FOLDER=/2pdf
RUN mkdir -p $ROOT_FOLDER && chmod 770 $ROOT_FOLDER
VOLUME $ROOT_FOLDER

RUN echo deb http://ftp.debian.org/debian/ stable main non-free contrib >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y \
    libreoffice-writer \
    openjdk-17-jre-headless \
    ttf-mscorefonts-installer \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/apk/*

COPY ./src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/pdftk ./usr/bin/

## install gettext and bash (required by start.sh)
#RUN apk add --no-cache gettext bash

# switch to non-root user
#USER $GUNICORN_USER_UID

#EXPOSE 80
#COPY docker-entrypoint.sh /
#RUN chmod 755 /docker-entrypoint.sh
#ENTRYPOINT ["/docker-entrypoint.sh"]

ADD ./src/main.py $ROOT_FOLDER/main.py
ENV PORT 8000
CMD ["python", "/2pdf/main.py"]