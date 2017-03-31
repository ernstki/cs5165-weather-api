# Create a container from Ubuntu.
#FROM python:3
#FROM alpine
FROM amancevice/pandas

EXPOSE 5000

# Credits.
MAINTAINER Kevin Ernst "ernstki@mail.uc.edu"

# Update distro's repositories.
#RUN apt-get update
#RUN apk update

# Install Python (these were for Debian-derived distros)
#RUN apt-get install -y -q build-essential
#RUN apt-get install -y python python-pip curl wget
#RUN apt-get install -y python-dev
#RUN apt-get install -y npm nodejs-legacy

# Install Python and build essentials (Alpine)
#RUN apk add --no-cache build-base
#RUN apk add --no-cache python python-dev py-pip 
# I /think/ this brings in npm
RUN apk add --no-cache nodejs

# Install any necessary (global) Python packages
RUN pip install virtualenv

# Install any necessary Node packages
RUN npm install -g bower

# Create a working directory.
RUN mkdir deploy

# Add requirements file.
ADD requirements.txt /deploy/requirements.txt

# Copy the Flask app's source and other necessary files
#COPY . /deploy/
ADD weatherapi /deploy/weatherapi/
ADD REST.md /deploy/
ADD .bowerrc /deploy/
ADD bower.json /deploy/
ADD startme.sh /startme.sh

# Set up virtualenv (allowing access to global 'site-packages')
WORKDIR /deploy
RUN virtualenv --system-site-packages venv
RUN venv/bin/pip install -r requirements.txt

# Run Bower installation
RUN bower --allow-root install

# Source: https://docs.docker.com/engine/reference/builder/#entrypoint
# See also: https://github.com/krallin/tini#using-tini
#ENTRYPOINT ["/sbin/tini", "--"]
CMD ["sh", "/startme.sh"]
