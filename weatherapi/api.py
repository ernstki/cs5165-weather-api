#!/usr/bin/env python
import os
import sys
import click
import pandas as pd
import numpy as np
from flask import Flask, Markup, request, render_template
from flask_restful import abort, reqparse, Resource, Api

app = Flask(__name__)
api = Api(app)  # Flask-Restful API object

app.config.update(
    TEMPLATES_AUTO_RELOAD=True,
    ERROR_404_HELP=False,
    CSV_FILE=os.path.join(app.root_path, 'static/daily.csv'),
    #EXPLAIN_TEMPLATE_LOADING=True,
)

# ref: http://pandas.pydata.org/pandas-docs/stable/io.html#specifying-column-data-types
weather = pd.read_csv(app.config['CSV_FILE'],
                      header=0,
                      dtype={'DATE': np.str})

# A request parser for the POST operation
postparser = reqparse.RequestParser(trim=True)
postparser.add_argument('DATE', type=str, required=True,
                         help='Invalid date (expected: YYYYMMDD as string)')
postparser.add_argument('TMIN', type=float, required=True,
                         help='Invalid temperature (expected: floating point)')
postparser.add_argument('TMAX', type=float, required=True,
                        help='Invalid temperature (expected: floating point)')


def check_date(date):
    """
    Check to see if the given date exists in the DataFrame. Abort if not.
    """
    if not date in weather[['DATE']].values:
        abort(404, message="No data found for %s" % date)


def add_date():
    """
    Add a new date given either a GET or a POST (application/json or
    application/x-www-form-urlencoded) request.
    """
    global weather
    args = postparser.parse_args()

    if args.DATE in weather[['DATE']].values:
        abort(400, message='Data for %s already exists' % args.DATE)

    s = pd.Series(args)
    assert s.any()
    weather = weather.append(s, ignore_index=True)

    return {'DATE': args.DATE}, 201


# props to https://stackoverflow.com/a/26961568
def df_to_reponse(df):
    """
    Make an 'application/json' reponse for a Pandas dataframe
    """
    # if there's only one record, un-arrayify it:
    if len(df) == 1:
        resp = df.iloc[0].to_json()
    else:
        # "orient='record'" removes the index from each record
        resp = df.to_json(orient='records')

    return app.response_class(resp, mimetype='application/json', status=200)


class Temps(Resource):
    dtypes = {'DATE': str, 'TMAX': float, 'TMIN': float}

    def get(self):
        """
        Return all dates for which weather data exists, unless query string
        parameters exist, in which case add the given date + temps.
        """
        if request.args:
            return add_date()
        else:
            global weather
            return df_to_reponse(weather[['DATE']])

    def post(self):
        """
        Add a new data to the weather database. Accepts application/json and
        application/x-www-form-urlencoded content types.
        """
        return add_date()


class Temp(Resource):

    def get(self, date):
        """
        Return temperature data for a single date
        """
        check_date(date)
        return df_to_reponse(weather[weather.DATE == date])

    def delete(self, date):
        """
        Delete the temperature data for a single date
        """
        check_date(date)
        weather.drop(weather.index[weather.DATE == '20170207'], inplace=True)
        return '', 204


api.add_resource(Temps, '/historical/')
api.add_resource(Temp, '/historical/<string:date>')

# ========================================================================
#                              r o u t e s
# ========================================================================

@app.route('/')
def index():
    from markdown import Markdown
    #from markdown import Markdown

    mdfile = os.path.join(app.root_path, '..', 'REST.md')
    with app.open_resource(mdfile, 'r') as f:
        sourcetext = unicode(f.read(), 'utf-8')

    # Borrowed from https://github.com/skurfer/RenderMarkdown
    md_ext = ['extra', 'codehilite']

    md = Markdown(extensions=md_ext, output_format='html5')

    # If you needed it, here's how to force a string into UTF-8 format.
    #     mdown = mdown.decode('utf8', 'ignore')
    # ...thanks, https://stackoverflow.com/a/20768800
    #markdown = Markup(linkify(md.convert(sourcetext), skip_pre=True))
    markdown = Markup(md.convert(sourcetext))

    return render_template('index.html', markdown=markdown)


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


if __name__ == '__main__':
    click.secho('\nPlease launch the demo API with\n', err=True)
    click.secho('    export FLASK_APP=api.py', bold=True,
                err=True)
    click.secho('    flask run [--host=X.X.X.X] [--port=YYYY]\n', bold=True,
                err=True)
    sys.exit(1)
