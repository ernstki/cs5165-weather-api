FROM alpine
MAINTAINER Kevin Ernst "ernstki@mail.uc.edu"

# Install Python and build essentials (Alpine)
RUN apk add --no-cache build-base
# https://stackoverflow.com/a/62555259
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python

# Install any necessary Node packages; Bower will require Git
RUN apk add --no-cache nodejs npm git
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
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt

# Run Bower installation
RUN bower --allow-root install

EXPOSE 5000

# Source: https://docs.docker.com/engine/reference/builder/#entrypoint
# See also: https://github.com/krallin/tini#using-tini
#ENTRYPOINT ["/sbin/tini", "--"]
CMD ["sh", "/startme.sh"]
