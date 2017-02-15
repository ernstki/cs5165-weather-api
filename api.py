#!/usr/bin/env python
import os
import sys
import click
import pandas as pd
import numpy as np
from flask import Flask, request, render_template
from flask_restful import abort, reqparse, Resource, Api

app = Flask(__name__)
api = Api(app)  # Flask-Restful API object

app.debug = True
app.config.update(
    TEMPLATES_AUTO_RELOAD=True,
    PROJECT_ROOT=os.path.abspath(os.path.dirname(__file__)),
    ERROR_404_HELP=False,
    #EXPLAIN_TEMPLATE_LOADING=True,
)

# ref: http://pandas.pydata.org/pandas-docs/stable/io.html#specifying-column-data-types
weather = pd.read_csv('static/daily.csv', header=0,
                      dtype={'DATE': np.str})

# A request parser for the POST operation
postparser = reqparse.RequestParser(trim=True)
postparser.add_argument('DATE', type=str,
                         help='Invalid date (expected: YYYYMMDD as string)')
postparser.add_argument('TMIN', type=float,
                         help='Invalid temperature (expected: floating point)')
postparser.add_argument('TMAX', type=float,
                        help='Invalid temperature (expected: floating point)')


def check_date(date):
    """
    Check to see if the given date exists in the DataFrame. Abort if not.
    """
    if not date in weather[['DATE']].values:
        abort(404, message="No data found for %s" % date)


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
        Return all dates for which weather data exists
        """
        return df_to_reponse(weather[['DATE']])

    def post(self):
        global weather
        args = postparser.parse_args()
        if args.DATE in weather[['DATE']].values:
            abort(400, message='Data for %s already exists' % args.DATE)

        s = pd.Series(request.get_json())
        weather = weather.append(s, ignore_index=True)

        return {'DATE': args.DATE}, 201


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
    return render_template('index.html')


@app.cli.command(with_appcontext=False)
def clean():
    """
    Clean up .pyc files (and other detritus)
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
