from setuptools import setup

with open('requirements.txt', 'r') as f:
    requires=[line for line in f.read().split("\n")
              if line and not line.startswith('#')]

setup(
    name='WeatherAPI',
    version='0.0.1',
    packages=[
        'weatherapi',
    ],
    install_requires=requires,
    package_data={
        'weatherapi': [
            'weatherapi/helpers/*.py',
            'weatherapi/static/*',
            'weatherapi/templates/*'
        ]
    },
    #entry_points='''
    #    [console_scripts]
    #    starter=flask_starter.cli:main
    #    # Also interesting:
    #    # [flask.command]
    #''',
)
