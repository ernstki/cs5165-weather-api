import os
import json
import unittest
import datetime as dt

import weatherapi

class WeatherApiTestCase(unittest.TestCase):
    headers = ('DATE', 'TMAX', 'TMIN')
   
    def _shift_date(self, d, delta=-1):
        """
        Take a date in "YYYYMMDD" format and subtract delta days; return the
        result as a string in the same format
        """
        if not (type(d) == str or type(d) == unicode):
            raise RuntimeError("'_shift_date' expects string input")

        _d = dt.datetime.strptime(d, '%Y%m%d')
        _d = _d + dt.timedelta(days=delta)
        return _d.strftime('%Y%m%d')


    def setUp(self):
        weatherapi.app.config['TESTING'] = True
        self.app = weatherapi.app.test_client()
        self.csvfile = weatherapi.app.config['CSV_FILE']

        with open(self.csvfile, 'r') as csv:
            headers = tuple(csv.readline().strip().split(','))
            self.assertEqual(headers, self.headers,
                             "CSV header row didn't match expected")

            self.data = []
            for line in csv.readlines():
                datum = line.strip().split(',')
                self.data.append( (str(datum[0]),
                                   float(datum[1]),
                                   float(datum[2])) )

        self.n = len(self.data)


    def test_shift_date(self):
        self.assertEqual(self._shift_date('20170301'), '20170228',
                         '_shift_date (delta=-1) helper function failed')
        self.assertEqual(self._shift_date('20170301', delta=-2), "20170227",
                         '_shift_date (delta=-2) helper function failed')
         

    def test_historical_get_redirect(self):
        rv = self.app.get('/historical')
        self.assertEqual(rv.status_code, 301,
                         "request to /historical endpoint didn't redirect")
        self.assertTrue(rv.headers['Location'].endswith('historical/'),
                        "request didn't redirect properly to 'historical/'")


    def test_historical_get(self):
        rv = self.app.get('/historical/')
        self.assertEqual(rv.status_code, 200,
                         'invalid status requesting /historical endpoint')
        self.assertEqual(self.n, len(json.loads(rv.data)), 
                         "length of JSON data didn't match CSV data")


    def test_get_one_date(self):
        d = self.data[0][0]
        rv = self.app.get('/historical/%s' % d)
        j = json.loads(rv.data)
        self.assertEqual(rv.status_code, 200,
                         "invalid status requesting date '%s'" % d)
        self.assertTrue(type(j['DATE']) is unicode or type(j['DATE']) is str,
                        'DATE is not unicode or str type')
        self.assertTrue(type(j['TMAX']) is int or type(j['TMAX']) is float,
                        'TMAX is not int or float type')
        self.assertTrue(type(j['TMIN']) is int or type(j['TMIN']) is float,
                        'TMIN is not int type')


    def test_new_date_get_query_string(self):
        pastd = self._shift_date(self.data[0][0], delta=-1)
        d = zip(self.headers, (pastd, self.data[0][1], self.data[0][2]))

        rv = self.app.get('/historical/', query_string=dict(d))
        j = json.loads(rv.data)

        self.assertEqual(rv.status_code, 201,
                         "invalid status code (%i) GETing new date '%s'"
                         % (rv.status_code, pastd))
        self.assertEqual(j['DATE'], pastd,
                         "unexpected response GETing new date '%s'" % pastd)


    def test_new_date_post_json(self):
        pastd = self._shift_date(self.data[0][0], delta=-2)
        d = zip(self.headers, (pastd, self.data[0][1], self.data[0][2]))
        jd = json.dumps(dict(d))

        rv = self.app.post('/historical/', data=jd,
                           content_type='application/json')
        j = json.loads(rv.data)

        self.assertEqual(rv.status_code, 201,
                         "invalid status code (%i) posting new date '%s'"
                         % (rv.status_code, pastd))
        self.assertEqual(j['DATE'], pastd,
                         "unexpected response posting new date '%s'" % pastd)


    def test_new_date_post_x_www_form_urlencoded(self):
        pastd = self._shift_date(self.data[0][0], delta=-3)
        d = zip(self.headers, (pastd, self.data[0][1], self.data[0][2]))

        # Werkzeug.Environbuilder's default content type is
        # x-www-form-urlencoded if you give it a dict for 'data'
        rv = self.app.post('/historical/', data=dict(d))
        j = json.loads(rv.data)

        self.assertEqual(rv.status_code, 201,
                         "invalid status code posting new date '%s'" % pastd)
        self.assertEqual(j['DATE'], pastd,
                         "unexpected response posting new date '%s'" % pastd)


    def test_new_date_missing_values(self):
        pastd = self._shift_date(self.data[0][0], delta=-4)
        d = zip(self.headers, (pastd, self.data[0][1], self.data[0][2]))

        # leave each of DATE, TMAX, TMIN off, in sequence and try to POST
        for k, v in zip(self.headers, range(0,3)):
            badd = filter(lambda x: x[0] != k, d)
            print(badd)
            rv = self.app.post('/historical/', data=dict(badd))
            j = json.loads(rv.data)

            self.assertEqual(rv.status_code, 400,
                            "expected error 400 when missing '%s'" % k)
            self.assertTrue('message' in j.keys(),
                            'expected error message in response')
            self.assertTrue(k in j['message'].keys(),
                            "expected '%s' in error message" % k)
                        

    def test_post_one_duplicate_date(self):
        d = dict(zip(self.headers, self.data[0]))

        # make sure we get a good response for this date
        rv = self.app.get('/historical/%s' % d['DATE'])
        j = json.loads(rv.data)
        self.assertEqual(rv.status_code, 200,
                         "expected status 200 fetching date '%s'" % d['DATE'])
        self.assertEqual(j['DATE'], d['DATE'])

        # make sure POSTing a duplicate gets an error of "already exists"
        rv = self.app.post('/historical/', data=d)
        j = json.loads(rv.data)
        self.assertEqual(rv.status_code, 400,
                         "expected error 400 posting dup date '%s'" % d['DATE'])
        self.assertTrue(j['message'].endswith('already exists'),
                        "unexpected error posting dup date '%s'" % d['DATE'])


    def test_get_non_existent_date(self):
        d = '99990101'
        rv = self.app.get('/historical/%s' % d)
        j = json.loads(rv.data)
        self.assertEqual(rv.status_code, 404,
                         "expected error 404 requesting future date '%s'" % d)
        self.assertTrue(j['message'].startswith('No data found'),
                        "expected 'No data found' error message")

    # the 'zz' is so that it runs at the end, otherwise assertions about the
    # size of the data read in from the .csv file will fail
    def test_zz_delete_date(self):
        d = self.data[0][0]
        rv = self.app.delete('/historical/%s' % d)
        self.assertEqual(rv.status_code, 204,
                         "invalid status requesting date '%s'" % d)
        self.assertTrue(not rv.data,
                        "request body should be empty for DELETE operation")


    def test_zz_delete_non_existent_date(self):
        d = '99990101'
        rv = self.app.delete('/historical/%s' % d)
        j = json.loads(rv.data)
        self.assertEqual(rv.status_code, 404,
                         "expected error 404 requesting future date '%s'" % d)
        self.assertTrue(j['message'].startswith('No data found'),
                        "expected 'No data found' error message")
    

if __name__ == '__main__':
    #suite = unittest.TestLoader().loadTestsFromTestCase(WeatherApiTestFixture)
    #unittest.TextTestRunner(verbosity=3).run(suite)
    unittest.main()
