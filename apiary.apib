FORMAT: 1A
HOST: http://cs5165ernstki.ddns.net/

# CS5165 Weather API

REST API for historical temperatures (highs and lows) in Cincinnati, O. For
Prof. Tatavarty's 17FS_CS5165 Cloud Computing course.

[A dynamic version][apiary] of this API documentation is available in
[API Blueprint][apibp] format at apiary.io. The Apiary docs includes a test
console capable of querying against API of the [live server on EC2][ec2].

<table class="table">
  <thead>
    <tr>
      <th align="left">Version</th><th align="left">Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td valign="top">1.0</td>
      <td>
        Spec matches v0.0.1 of <code>weatherapi</code> code
      </td>
    </tr>
    <tr>
      <td valign="top">0.1</td><td>Creation of Apiary Project</td>
    </tr>
  </tbody>
</table>

[Source code][source] on GitHub, [MIT licensed][license].

[apiary]: http://docs.cs5165weatherapi.apiary.io
[apibp]: https://apiblueprint.org/documentation/specification.html
[ec2]: http://cs5165ernstki.ddns.net
[source]: https://github.com/ernstki/cs5165-weather-api
[license]: https://github.com/ernstki/cs5165-weather-api/blob/master/LICENSE.txt


## Historical Temperatures Collection [/historical/]

The `/historical` resource allows you to retrieve temperature data for all
dates in the database, or POST temperature data for a new date.

The Weather API will accept both the GET and POST methods for adding new data
to the database. For POST, both `application/json` and
`application/x-www-form-urlencoded` content types are accepted. (For the GET
method, see below.)

Attempting to POST to a date that already exists in the database will yield
a `Data for <date> already exists` message in the JSON response.


### Get all historical temperatures [GET]

+ Response 200 (application/json)

        [
          {
            "DATE": "20130101"
          },
          {
            "DATE": "20130102"
          },
          {
            "DATE": "20130103"
          },
          {
            "DATE": "20170208"
          },
          {
            "DATE": "20170209"
          }
        ]

### Add temperature data for a date - POST [POST]


+ Request (application/json)

    **Note**: Content type `application/x-www-form-urlencoded` is also accepted
    for POST requests.

    + Body

            { "DATE": "20170215", "TMAX": 62.0, "TMIN": 45.0 }


+ Response 201 (application/json)

    + Body

            {
                "DATE": "20170215"
            }

+ Request (application/json)

    When attempting to temperature data for date **already in the database**
    with a POST request, you get an error in the JSON response.

    + Body

            { "DATE": "20170215", "TMAX": 62.0, "TMIN": 45.0 }


+ Response 400 (application/json)

    + Body

            {
                "message": "Data for 20170215 already exists"
            }
            

## Temperature Data - Add/Retrieve a Single Day [/historical/{date}]

The temperature data for a single date in the past is retrieved by adding
`{date}` in ISO8601 format (`YYYYMMDD`) to the end of the `/historical/`
resource.

Attempting to retrieve dates which don't exist in the datbase will yield
a `Data for <date> already exists` message in the JSON response.

+ Parameters

    + date (string) - date for which to fetch data (`YYYYMMDD` format)

### Get temperatures for a single day in the past [GET]

+ Response 200 (application/json)

    + Body

            {
                "DATE": "20170215",
                "TMAX": 62.0,
                "TMIN": 45.0
            }
            
+ Response 404 (application/json)

    When attempting to get temperatures for a day **not in the database**, you
    get an error message in the JSON response.
    
    + Body 

            {
                "message": "No data found for 99990101"
            }
            
### Delete temperature for a single day [DELETE]

+ Response 204

+ Response 404 (application/json)

    When attempting to delete the record for a day **not in the database**, you
    get an error message in the JSON response.
    
    + Body

            {
                "message": "No data found for 99990101"
            }


## Add New Data with GET Request [/historical/{?DATE,TMAX,TMIN}]

For adding new data to the database, the POST method probably makes more sense
semantically-speaking, but transmitting the date, max, and min temperatures as
query string parameters (_i.e._ after a `?` in the URL) also works.

As with the `POST` method above, attempting add a date that already exists
with a `GET` request will yield a `Data for <date> already exists` message in
the JSON response.

+ Parameters

    + DATE (string) - date for which to add data (`YYYYMMDD` format)
    + TMAX (int) - maximum temperature (&deg;F)
    + TMIN (int) - minumum temperature (&deg;F)
    
### Add temperature data for a date - GET [GET]

+ Response 201 (application/json)

    + Body

            {
                "DATE": "20170215"
            }

+ Response 400 (application/json)

    When attempting to temperature data for date **already in the database**
    with a GET request, you get an error in the JSON response.

    + Body

            {
                "message": "Data for 20170215 already exists"
            }