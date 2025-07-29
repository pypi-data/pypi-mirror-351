import sqlite3

# For each Day: sunrise, sunset, camp_prep_hours
#   Calc camp_arrive_time: sunset - camp_prep_hours

# For each Segment:
# GIVEN: segment_name(key), distance, aeg, ael, (maxElev, minElev)
# ESTIMATE: pace,
# CALCULATE:  hours, minutes

{'GC Escalante':
 {'day 1':
  {'Tanner': {'distance': 7.2, 'aeg': 414, 'ael': -5079, 'est_pace': 60}},
  {'d-1b':   {'distance': 2.69,'aeg': 192, 'ael': -237, 'est_pace': 60}}
  },
 {'day 2':
  {'d2-a': {'distance': 8.85, 'aeg': 2276, 'ael': -2374, 'est_pace': 60}},
  #!{'75-ck': {'distance': 5.44+0.83, 'aeg': 1497+285, 'ael': -1525 + -64,
  #!           'est_pace': 60}},
  #!{'Papago wall':{'distance': .74, 'aeg': 205, 'ael': -169, 'est_pace': 60}},
  },
 {'day 3':
  {'d3': {'distance': 6., 'aeg': 4742, 'ael': -271, 'est_pace': 60}},
  {'TH to Car': {'distance': 1.27, 'aeg': 135, 'ael': -1, 'est_pace': 20}},
  }
 }


# Calculate time (minutes) to hike a segment
class HikeTime():
    def __init__(self, distance, aeg, ael):
        self.distance = distance  # miles
        self.aeg = aeg # Accumulated Elevated Gain (feet)
        self.ael = aeg # Accumulated Elevated Loss (feet)

    def miles_to_km(miles):
        return miles * 1.60934

    def feet_to_m(feet):
        return feet * 0.3047992424196

    @property
    def nasmiths_time(self):
        # hrs = dist/3 + ascent/2000
        minutes = self.distance*60/3 + aeg*60/2000 - ael*60/2000
        return minutes

    @property
    def book_time(self):
        return 30*self.distance + 30*aeg/1000

    @property
    def munter_walkup_time(self):
        # hours =  (DISTANCE [km] + (ELEVATION [m]/100)) / RATE
        # Rate = 2. Off-trail travel (Bushwhacking)
        # Rate = 4. Walking or skiing uphill
        # Rate = 6. Walking downhill
        # Rate = 10. Skiing downhill
        rate = 4
        hours = (miles_to_km(self.distance) + feet_to_m(self.aeg)/100)/rate
        return hours*60

    @property
    def munter_walkdown_time(self):
        rate = 6
        hours = (miles_to_km(self.distance) + feet_to_m(-1*self.aegl/100)/rate
        return hours*60

    @property
    def munter_offtrail_time(self):
        rate = 2
        hours = (miles_to_km(self.distance) + feet_to_m(self.aeg)/100)/rate
        return hours*60

    # END class HikeTime

def create_db(dbfile="hike_segments.db"):
    con = sqlite3.connect(dbfile)
    cur = con.cursor()
    cur.exeucte("CREATE TABLE segment(name, distance, aeg, ael)")
    return cur

# lat,lon used for sunrise/set.  e.g. of end of day (camp or car)
# https://sunrisesunset.io/api/
# https://api.sunrisesunset.io/json?lat=38.907192&lng=-77.036873&timezone=UTC&date_start=1990-05-01&date_end=1990-07-01
def ingest_seg(segment_name, distance, aeg, ael,
               pace: int | None = None,  # minutes/mile
               minElev=None,
               maxElev=None,
               ):
    record = dict(name=segment_name,
                  distance=distance,
                  aeg=aeg,
                  ael=ael)
    cur = create_db()
    cur.execute("INSERT INTO segment VALUES (:name, :distance, :aeg, :ael)",
                (record,))

# "camp" is the end of the last segment for a day.  It might be the car.
def ingest_day(camp_name: str,
               camp_lat: float, # decimal degrees
               camp_lon: float, # decimal degrees
               camp_prep_hours: int = 2,
               ):
    sunrise = None  # for lat/lon
    sunset  = None  # for lat/lon
