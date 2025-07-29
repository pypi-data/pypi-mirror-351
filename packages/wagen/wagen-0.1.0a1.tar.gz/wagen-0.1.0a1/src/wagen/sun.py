import requests
import datetime as dt

# For much simpler retrieve of sunrise/set/twilights see:
# https://api.sunrise-sunset.org/json?lat=36.7201600&lng=-4.4203400
# {
#   "results": {
#     "sunrise": "5:08:31 AM",
#     "sunset": "7:19:35 PM",
#     "solar_noon": "12:14:03 PM",
#     "day_length": "14:11:04",
#     "civil_twilight_begin": "4:41:03 AM",
#     "civil_twilight_end": "7:47:02 PM",
#     "nautical_twilight_begin": "4:05:43 AM",
#     "nautical_twilight_end": "8:22:22 PM",
#     "astronomical_twilight_begin": "3:27:28 AM",
#     "astronomical_twilight_end": "9:00:38 PM"
#   },
#   "status": "OK",
#   "tzid": "UTC"
# }
#
# https://aa.usno.navy.mil/data/api
# https://aa.usno.navy.mil/api/rstt/oneday?date=2025-05-15&coords=36.08695,%20-111.86464&tz=-7
# Results with fields I don't care about removed
# {
#   "apiversion": "4.0.1",
#   "geometry": { "coordinates": [-111.86464,  36.08695 ],  },
#   "properties": {
#     "data": {
#       "closestphase": {
#         "day": 12, "month": 5, "phase": "Full Moon",
#         "time": "09:56",  "year": 2025
#       },
#       "curphase": "Waning Gibbous",
#       "day": 15,
#       "day_of_week": "Thursday",
#       "fracillum": "91%",
#       "isdst": false,
#       "label": null,
#       "month": 5,
#       "moondata": [
#         {"phen": "Set",  "time": "07:06"},
#         {"phen": "Rise", "time": "22:47"}
#       ],
#       "sundata": [
#         {"phen": "Begin Civil Twilight",  "time": "04:53"},
#         {"phen": "Rise", "time": "05:21"},
#         {"phen": "Set", "time": "19:27"},
#         {"phen": "End Civil Twilight", "time": "19:56"}
#       ],
#       "tz": -7.0,
#       "year": 2025
#     }
#   },
# }

def sun_from_lat_lon(lat: float,
                     lon: float,
                     date: int | str ='today',  # YYYYMMDD
                     tzid: str = 'America/Phoenix'
                     ):
    formatted: int = 0
    # See https://sunrise-sunset.org/api
    # Parameters: lat, lng, date, callback, formatted, tzid
    url = (f'https://api.sunrise-sunset.org/json?'
           f'date={date}&lat={lat}&lng={lon}'
           f'&formatted={formatted}&tzid={tzid}'
           )
    #! print(f'Using {url=}')
    response = requests.get(url)
    result = response.json()
    sdict = result['results']
    day_length = sdict['day_length']   # minutes
    del sdict['day_length']
    sundatetimes = {k:dt.datetime.fromisoformat(v) for k,v in sdict.items()}
    sundatetimes['day_length'] = day_length
    return sundatetimes

def sun_set_rise(lat: float,
                 lon: float,
                 date: str | None=None,  # YYYY-MM-DD. default=today
                 tzid: str = 'America/Phoenix',
                 formatted: int = 1  # 1 for simple local time for TZID; else ISO
                 ):
    """Intended for CAMP lat/lon. Get sunset for DATE and sunrise for NEXT DAY.
    """
    arrive_day = dt.date.today() if date is None else dt.date.fromisoformat(date)
    #! print(f'{lat=}, {lon=}, {date=}')
    #! print(f'{arrive_day=}')
    depart_day = arrive_day + dt.timedelta(days=1)
    sunset = sun_from_lat_lon(lat, lon,
                              date=str(arrive_day),
                              tzid=tzid)['sunset']
    twilight = sun_from_lat_lon(lat, lon,
                               date=depart_day,
                               tzid=tzid)['civil_twilight_begin'] # 6 degree
    sunrise = sun_from_lat_lon(lat, lon,
                               date=depart_day,
                               tzid=tzid)['sunrise']


    return  (sunset, twilight, sunrise)
