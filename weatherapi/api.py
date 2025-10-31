#!/usr/bin/env python
import os
import sys
import re
import click
import pandas as pd
import numpy as np
from markupsafe import Markup
from flask import (Flask as Flask_, Request as Request_, Response,
                   render_template, jsonify)
from flask_restful import abort, reqparse, Resource, Api
from werkzeug.exceptions import BadRequestKeyError

from .helpers import register_jinja_helpers


# https://github.com/python-restx/flask-restx/issues/454#issuecomment-1185615974
class Request(Request_):
    def get_json(self, *args, **kwargs):
        kwargs.update(silent=True)
        return super().get_json(*args, **kwargs)


class Flask(Flask_):
    request_class = Request


app = Flask(__name__)
api = Api(app)  # Flask-Restful API object

register_jinja_helpers(app)

app.config.update(
    TEMPLATES_AUTO_RELOAD=True,
    ERROR_404_HELP=False,
    CSV_FILE=os.path.join(app.root_path, 'static/daily.csv'),
    #EXPLAIN_TEMPLATE_LOADING=True,
)

# ref: http://pandas.pydata.org/pandas-docs/stable/io.html#specifying-column-data-types
weather = pd.read_csv(app.config['CSV_FILE'],
                      header=0,
                      dtype={'DATE': str})


# A request parser for GETs and POSTs (the entire date object, all keys req'd)
date_parser = reqparse.RequestParser(trim=True)
date_parser.add_argument('DATE', type=str, required=True, location='json',
                         help='Invalid date (expected: YYYYMMDD as string)')
date_parser.add_argument('TMIN', type=float, required=True, location='json',
                         help='Invalid temperature (expected: floating point)')
date_parser.add_argument('TMAX', type=float, required=True, location='json',
                         help='Invalid temperature (expected: floating point)')

# Same parser, but with all arguments optional (used to check which ones exist)
date_parser_optional = date_parser.copy()
for arg in ['DATE', 'TMIN', 'TMAX']:
    date_parser_optional.replace_argument(arg, required=False)

# A request parser for the ?limit=n query string param for /forecast
limit_parser = reqparse.RequestParser(trim=True)
limit_parser.add_argument('limit', type=int, required=False)


def check_date(date):
    """
    Check to see if the given date exists in the DataFrame. Abort if not.
    """
    if not date:
        abort(500, message="Error checking date (null input value)")
    if not re.match(r'\d{8}$', date):
        abort(400, message="Invalid date '%s'; did not match pattern" % date)
    if not date in weather[['DATE']].values:
        abort(404, message="No data found for %s" % date)


def add_date():
    """
    Add a new date given either a GET or a POST (application/json or
    application/x-www-form-urlencoded) request.
    """
    global weather
    args = date_parser.parse_args()  # will abort if any are missing

    # Want to abort if the DATE already exists in the database? Here's how:
    #if args.DATE in weather[['DATE']].values:
    #    abort(400, message='Data for %s already exists' % args.DATE)

    s = pd.Series(args)
    if not s.any():
        abort(500, message="Internal server error adding new date")

    weather = weather.append(s, ignore_index=True).sort()
    return {'DATE': args.DATE}, 201


# props to https://stackoverflow.com/a/26961568
def df_to_response(df):
    """
    Make an 'application/json' response for a Pandas dataframe
    """
    # if there's only one record, un-arrayify it:
    if len(df) == 1:
        resp = df.iloc[0].to_json()
    else:
        # "orient='record'" removes the index from each record
        resp = df.to_json(orient='records')

    return app.response_class(resp, mimetype='application/json', status=200)


class Temps(Resource):
    """
    Access to all historical data; POST to add new records
    """
    dtypes = {'DATE': str, 'TMAX': float, 'TMIN': float}

    def get(self):
        """
        Return all dates for which weather data exists, unless query string
        parameters exist.

          - if *no* query arguments, then return all data
          - if *only* DATE exists in the query args, return data for that date
          - otherwise add the given date + temps
        """
        global weather
        args = date_parser_optional.parse_args()
        app.logger.info("GET request parsed args: %s" % args)

        # what we normally expect; no query string args, return all dates
        if not any(args.values()):
            return df_to_response(weather[['DATE']])

        # if DATE and only DATE in query string:
        if not args.TMIN and not args.TMAX:
            check_date(args.DATE)  # maybe overkill?
            return df_to_response(
                weather[weather.DATE == args.DATE]
            )
        else:
            # This will report any missing keys with a 400 response
            return add_date()


    def post(self):
        """
        Add a new data to the weather database. Accepts application/json and
        application/x-www-form-urlencoded content types.
        """
        return add_date()


class Temp(Resource):
    """
    Access to a single date in ISO8601 (YYYYMMDD) format
    """

    def get(self, date):
        """
        Return temperature data for a single date
        """
        check_date(date)
        return df_to_response(weather[weather.DATE == date])

    def delete(self, date):
        """
        Delete the temperature data for a single date
        """
        check_date(date)
        weather.drop(weather.index[weather.DATE == date], inplace=True)
        return '', 204


class FutureForecast(Resource):

    def get(self):
        abort(501, message="Not yet implemented :(")


class Forecast(Resource):
    """
    Weather forecasts
    """

    def get(self, date):
        """
        Return weather forecast for next seven days
        """

        args = limit_parser.parse_args()
        limit = args.limit if args.limit else 7

        check_date(date)
        starti = weather.index[weather.DATE == date][0]
        return df_to_response(weather[starti:starti + limit])


api.add_resource(Temps, '/historical/')
api.add_resource(Temp, '/historical/<string:date>')
api.add_resource(FutureForecast, '/forecast/')
api.add_resource(Forecast, '/forecast/<string:date>')

# ========================================================================
#                              r o u t e s
# ========================================================================

@app.route('/')
def index():
    """
    Main site: API documentation in HTML format
    """
    from markdown import Markdown
    #from markdown import Markdown

    mdfile = os.path.join(app.root_path, '..', 'REST.md')
    with app.open_resource(mdfile, 'r') as f:
        #sourcetext = unicode(f.read(), 'utf-8')
        sourcetext = f.read()

    # Borrowed from https://github.com/skurfer/RenderMarkdown
    md_ext = ['extra', 'codehilite']

    md = Markdown(extensions=md_ext, output_format='html5')

    # If you needed it, here's how to force a string into UTF-8 format.
    #     mdown = mdown.decode('utf8', 'ignore')
    # ...thanks, https://stackoverflow.com/a/20768800
    #markdown = Markup(linkify(md.convert(sourcetext), skip_pre=True))
    markdown = Markup(md.convert(sourcetext))

    return render_template('index.html.j2', markdown=markdown)


@app.route('/license')
def license():
    """
    Return the LICENSE.txt to the browser
    """
    with app.open_resource(os.path.join('..', 'LICENSE.txt')) as f:
        return Response(f.read(), mimetype='text/plain')


@app.route('/help')
def help():
    """
    *You are here: help on available endpoints
    """
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            docstring = app.view_functions[rule.endpoint].__doc__

            if not docstring:
                docstring = "No help provided for endpoint"

            func_list[rule.rule] = docstring.strip().split('\n')[0]
    return jsonify(func_list)


@app.cli.command(with_appcontext=False)
def test():
    """
    Runs automated (unittest) tests
    """
    os.system('python -m unittest -b -v tests')


@app.cli.command(with_appcontext=False)
def clean():
    """
    Cleans up .pyc files (and other detritus).
    """
    click.secho('Tidying up the project directories...', fg='yellow')
    os.chdir(app.config['PROJECT_ROOT'])
    for subdir in ['.', 'templates', 'static/css', 'static/js']:
        try:
            click.secho('  - %s' % subdir)
            os.system("rm %s/*.pyc" % subdir)
            os.system("rm -rf %s/__pycache__" % subdir)
            os.system("rm %s/.*.un~" % subdir)
        except:
            click.secho('    Oops. A failure occurred cleaning %s' % subdir,
                        fg='red')

    click.secho('\nAll done.', fg='green')


@app.cli.command()
@click.option('--restrict-date-range', type=click.STRING)
@click.option('--with-ids', is_flag=True, default=False,
              help='Include unique IDs with each record.')
@click.option('--as-csv', is_flag=True, default=False,
              help='Dump in comma-separated value format.')
def dumpdb(with_ids, as_csv):
    """Dump contents of database to the terminal."""
    pass

    #sep = '\t'

    #if as_csv:
    #    with_ids = True
    #    sep = ','
    #    cols = [col.name for col in Organism.__table__.columns]

    #    click.echo(','.join(cols))

    #for rec in Organism.query.all():
    #    cols = [rec.name]

    #    if with_ids:
    #        cols.insert(0, str(rec.id))

    #    click.echo(sep.join(cols))


if __name__ == '__main__':
    click.secho('\nPlease launch the demo API with\n', err=True)
    click.secho('    export FLASK_APP=api.py', bold=True,
                err=True)
    click.secho('    flask run [--host=X.X.X.X] [--port=YYYY]\n', bold=True,
                err=True)
    sys.exit(1)
