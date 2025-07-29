"""Create timeline for hike/adventure that uses estimated pace to predict
time to reach each waypoint. Use given day start time or a start derived from sunrise local to hike. Warn if estimate camp arrival is too close to sunset."""

import csv
from pathlib import Path
import datetime as dt
from pprint import pp

import pandas as pd

from wagen import sun
import wagen.caltopo_io as cti


# given start time for each day, calc end time and hours from sunset!!!
# Get elevation (meters) from lat,lon
# https://api.open-elevation.com/api/v1/lookup?locations=41.161758,-8.583933
def timeline(trip_df, trip,
             start_time: dt.datetime | None = None, # sunrise today
             tzid: str = 'America/Phoenix',
             morning_daylight: float=1.5, # reqd hours @ camp after twilight
             evening_daylight: float=2.0, # reqd hours @ camp before sunset
             include_dt = False,
             rename = False,
             ):
    """Assume hiking will start the same time every day.
    Consider adding "BEGIN" waypoint for day specific start time!!!
    """
    #!print(f'timeline: {trip=} {start_time=} {tzid=} {morning_daylight=} {evening_daylight=} {include_dt=}')

    trip_meta = trip.copy()
    df = trip_df.copy(deep=True)
    day_minutes = 0
    prev_done_time = None
    eod = False

    lat, lon = trip['start_latlon']
    sunset, twilight, sunrise = sun.sun_set_rise(
        lat,
        lon,
        date=str(start_time)[:10].replace('-',''),
        tzid=tzid,
        formatted=0)

    # Modify start_time if does not contain both date and meaningful time.
    if start_time is None:
        start_time = dt.datetime.today()

    if start_time.hour == 0 and start_time.minute == 0:
        start_time = start_time.replace(hour=twilight.hour,
                                        minute=twilight.minute,
                                        tzinfo=twilight.tzinfo,
                                        second=0, microsecond=0)
        start_time += dt.timedelta(hours=morning_daylight)


    first_date = start_time.date()
    day_start_time = start_time.time()
    trip_meta = dict(
        first_date=first_date.isoformat(),
        day_start_time=day_start_time.strftime("%H:%M"),
        twilight=twilight.isoformat(),
        sunrise=sunrise.isoformat(),
        sunset=sunset.isoformat(),
        start_latlon=trip['start_latlon'],
        start_elevation=trip['start_elevation'],
        morning_daylight=morning_daylight,
        evening_daylight=evening_daylight,
        tzid=tzid,
        )

    for index, row in trip_df.iterrows():
        # Only do this on the first segment Start of the day
        if row['waypoint'] == 'Start' and eod:
            day_minutes = 0
            eod = False
        day_minutes += row.duration + row.break_minutes
        #!df.at[index, 'day_minutes'] = day_minutes
        row_dt = (dt.datetime.combine(first_date,
                                      day_start_time,
                                      sunrise.tzinfo)
                  + dt.timedelta(days=row['day']-1, minutes=day_minutes))
        #!!! df.at[index, 'deviation'] = row_dt.date()
        # see: https://docs.google.com/spreadsheets/d/1-DNLDEDKi286bAzVmbptdajS_mAE8OeM1oqFAemgrF4/edit?usp=sharing

        if (row_dt.time() > (sunset
                             - dt.timedelta(hours=evening_daylight)).time()):
            df.at[index, 'alert'] = "LATE to CAMP"
        else:
            df.at[index, 'alert'] = ''


        df.at[index, 'date'] = row_dt.date()
        done_time = row_dt.time()
        ldt = '' if prev_done_time == done_time else done_time.strftime("%H:%M")
        prev_done_time = done_time
        df.at[index, 'time'] = ldt
        df.at[index, 'day_hours'] = day_minutes/60.0
        df.at[index, 'dt'] = row_dt

        #!if row['waypoint'] in ['camp','car']: # 'EOD':
        if row['waypoint'] in ['camp','car']:
            eod = True
    # END for trip_df.iterrows

    final_column_order = ['date','time','alert', 'day', 'waypoint',
                          'distance', 'aeg','ael','day_hours',
                          'duration', 'break_minutes', 'elapsed',
                          'elevation', 'hours', 'pace',
                          # 'segment', 'trip_leg',
                          ]
    if include_dt:
        final_column_order.append('dt')

    df = df[final_column_order]

    #df.drop(['segment','dt', 'day'], axis="columns", inplace=True)
    if rename:
        renames = {c: c.title() for c in df.columns}
        renames.update({
            'distance': 'Distance (miles)',
            'aeg': 'AEG (ft)',
            'ael': 'AEL (ft)',
            'day_hours': 'Day Travel Time (hrs)',
            'duration': 'Leg Travel Time (mins)',
            'break_minutes': 'Leg Break (mins)',
            'pace': 'Pace (mins/mi)',
            })
        df.rename(columns=renames, inplace=True)
        df.set_index(['Date', 'Time'], inplace=True)
    return df, trip_meta

def trip_timeline(csvfname, **kwargs):
    caltopo_df, trip = cti.travelplan_multi_csv(csvfname)
    df, meta = timeline(caltopo_df, trip, **kwargs)
    return df, trip, meta
