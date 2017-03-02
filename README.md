# 17FS_CS5165 Weather API
CS5165 Homework #2 - Weather REST API

[Live server](http://cs5165ernstki.ddns.net) | 
[API specification](http://docs.cs5165weatherapi.apiary.io)
([Apiary Blueprint][apiarybp] format, with interactive console)

## Assignment 

Your assignment will be graded on the following metrics:

* <strike>Does the output conform exactly to the specifications?</strike>
* <strike>Is the [REST.md](REST.md) well-formatted markdown and
  complete?</strike>
* <strike>Are the HTTP codes correct ? Example - 200 for OK. 201 for created.
  404 for not found and so on.</strike>
* <strike>Does the REST API accept the inputs as GET or POST
  parameters?</strike>
* <strike>Is the result well-formed (does it adhere to JSON or XML standards) and
  returned as an HTTP 200 “Ok” result?</strike>
* <strike>Does the REST API yield results consistent with the same
  data?</strike>

You will also need to add a [`REST.md`](REST.md) “markdown” document to your
GitHub, and document the resources in your API, the input parameters
+ data-types they accept, and the parameters &amp; data-types that will be in
the results.

## System Requirements

* Python 2.7.x (3.x untested)
* virtualenv
* pip

These should part of most standard Python kits. Try typing `virtualenv --help`
or `pip --help` at the command line to see if they're already installed on your
system.

## Installation

1. Clone (or download) this repository and generate a fresh virtual
   environment:

    ```
    # replace <githost> with either github.com or github.uc.edu
    git clone git@<githost>:ernstki/cs5165-weather-api.git

    # change into the repository's base directory
    cd cs5165-weather-api

    # create a virtual environment, into which you'll install all the
    # dependencies for this project
    virtualenv venv

    # on Windows, do 'venv\scripts\activate.cmd' (I think)
    source venv/bin/activate
    ```

2. Install necessary Python packages using `pip`:

    ```
    pip install --editable .

    # possibly also works:
    pip install -r requirements.txt
    ```

3. Launch the Flask web application:

    ```
    # on Windows, do 'set FLASK_APP=demoapi\demoapi.py' (note the backslash)
    export FLASK_DEBUG=1
    export FLASK_APP=demoapi/demoapi.py
    flask run  # defaults to http://127.0.0.1:5000
    ```

    If you install [autoenv] on a Unix system (OS X / macOS is Unix), you don't
    have to set `FLASK_APP`, it's done for you automatically when you enter the
    directory.

    If you're running the Flask application within a VirtualBox VM, you'll want
    to be sure that the app runs on 0.0.0.0, so that the VirtualBox port
    forwarding works correctly. You can launch the app with command line flags
    to achieve that:

    ```
    flask run --host=0.0.0.0  # optionally: --port=5000
    ```

## Running automated tests

The automated tests cover only the requirements of the assignment, and don't
check any aspect of the web front-end.

```
flask test

# alternatively, prettier:
pip install pytest
pytest tests
```

## Other tips

### Testing the API with [Postman][]

You can use [Postman][] to test requests to the API. The included
[`postman_collection_v1.json`](postman_collection_v1.json) may be imported
through the Postman user interface, and includes some example queries.

## Credits
Incorporates [Glyphicons][] and [Bootstrap][] CSS / JS source files, both
under the terms of the MIT license ([ref1][glyphlicense], [ref2][bslicense]).

&copy;2017 Kevin Ernst, [MIT licensed](LICENSE.txt).

[apiarybp]: https://apiblueprint.org/documentation/specification.html
[autoenv]: https://github.com/kennethreitz/autoenv
[postman]: https://www.getpostman.com/apps
[glyphicons]: https://glyphicons.com/
[bootstrap]: https://getbootstrap.com/
[glyphlicense]: https://glyphicons.com/license/
[bslicense]: https://github.com/twbs/bootstrap/blob/master/LICENSE
