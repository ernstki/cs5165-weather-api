FROM alpine
MAINTAINER Kevin Ernst "ernstki@mail.uc.edu"

# Install Python and build essentials (https://stackoverflow.com/a/62555259)
# Install any necessary Node packages; Bower will require Git
#RUN apk add --no-cache build-base && \
RUN apk add --update --no-cache python3 && \
    ln -sf python3 /usr/bin/python
RUN apk add --no-cache nodejs npm git && \
    npm install -g bower

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
RUN bower -f install
# Build minified Vue library because ¯\_(ツ)_/¯
WORKDIR /deploy/weatherapi/static/vendor/vue
# pnpm works around some dumb error in the package.json
# source: https://stackoverflow.com/a/78927532
RUN npm install -g pnpm && \
    pnpm install
# source: https://bobbyhadz.com/blog/javascript-heap-out-of-memory
# the default appears to be 1.4 GB regardless of system RAM
# (source: https://dev.to/evle/what-exactly-is-the-memory-limit-of-nodejs-4cpi)
RUN NODE_OPTIONS=--max-old-space-size=4096 pnpm build
# clean up after the 'npm build'
RUN rm -rf node_modules packages src test && \
    rm -rf /root/.local/share/pnpm /root/.cache /root/.npm

# clean up some more
RUN npm uninstall -g pnpm && \
    apk del nodejs npm git && apk del

WORKDIR /deploy
EXPOSE 5000

# Source: https://docs.docker.com/engine/reference/builder/#entrypoint
# See also: https://github.com/krallin/tini#using-tini
#ENTRYPOINT ["/sbin/tini", "--"]
CMD ["sh", "/startme.sh"]
