import os
import unittest

import weatherapi

class WeatherApiTestCase(unittest.TestCase):

    def setUp(self):
        weatherapi.app.config['TESTING'] = True
        self.app = weatherapi.app.test_client()
        self.csvfile = weatherapi.app.config['CSV_FILE']

        with open(self.csvfile, 'r') as csv:
            self.n = len(csv.readlines())

    def tearDown(self):
        pass

    def test_historical_get(self):
        rv = self.app.get('/historical')


if __name__ == '__main__':
    unittest.main()
