"""Convert data from ColTopo (CT) to easier formats for calculation.

Segment :: (seg) a line in CT, typically depicting a route or trail.
Leg :: A portion of a segment ending with a labeled waypoint.
   But ONLY if waypoint is close to segment line.
Day :: A sequence of Segments intended to be traveled in a day. (but
   we might have to change our mind!)

Break :: (e.g. for rest) is specified in Marker/Comments with e.g. "20 min"
  It will show as Leg=Break in Travel Plan and be included in accum trav time.

Add some useful columns: segment, break_minutes
Add some useful Waypoints:
  camp|car :: waypoint at end of a day
"""
# See also: backpack-planning-artifacts.org
import csv
from pathlib import Path
import pandas as pd
import datetime as dt

def hr_min2minutes(hrmin):
    "Convert '5 hr 17 min' or '10 min' to int minutes"

    iterators = [iter(hrmin.split())] * 2
    dur = {k:int(v) for v,k in zip(*iterators, strict=True)}
    minutes = dur.get('hr',0)*60 + dur.get('min',0)
    return minutes

normal_rec = {
    'Leg': '0',
    'Gain': "+0'",
    'Loss': "-0'",
    'Distance': '0 ft',
    'Leg Time': '0 min',
    'Total Time': '0 min',
    }

# To pprint csv in linux:
#   echo "WP,LEG,LAT,LON,ELEV,GAIN,LOS,DIST,BEAR,LTIME,TTIME,NOTES" >hdr.csv
#   cat hdr.csv travelplan.GC-LCR-noraft.csv | column  -t -s,
# Extract from CalTopo Travel Plan CSV file (single segment)
def travelplan_multi_csv(csvfname='~/Downloads/travelplan.csv',
                         excelfname=None):
    """CSV file produced by:
    + click on line Bulk Ops
    + ctl-click on segments (labels) to include
      Click in the order they should be in the report.
    + Travel Plan
    + OPTIONAL: modify Travel mode and associated values for any Segement.
       This will affect the Leg and Total hike times.
    + Export to CSV.

    The resulting CSV has formatting issues interfer with calculations.
    This function tries to eliminate those issues.

    RETURN: pd.DataFrame
    """
    records = list()
    eod = False # End Of Day
    total_minutes = 0
    total_distance = 0
    prev = dict()
    new_rec = None
    trip_leg = 0
    elapsed_minutes = 0
    camp_cnt = 0
    day = travel_day = 1
    start_latlon = None

    header = ['Waypoint',    # the Label on a CT Marker
              'Leg',         # int; ID of leg within a segment (excludes Breaks)
              'Coordinates', # IGNORED; lat,lon
              'Elevation',   # (feet) of Waypoint
              'Gain',        # (feet) Accumulated Elevation Gain (aeg) over Leg
              'Loss',        # (feet) Accumulated Elevation Loss (ael) over Leg
              'Distance',    # (miles) Traveled distance over Leg
              'Bearing',     # IGNORED; nnnDegrees TN (True North)
              'Leg Time',    # (minutes) Traveled time over Leg
              'Total Time',  # (hrs:min) Accumulated travel time over Segment
              'Notes',
              ]

    with open(Path(csvfname).expanduser(), newline='') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=header)
        for rec in reader:
            # deal with special rows that to match the header
            if not any(rec.values()):  # empty row
                continue
            if not any(list(rec.values())[1:]):
                # If only a Waypoint value in row, we have new new Segment.
                seg_name = rec['Waypoint']
                continue
            if rec['Leg'] == 'Break':
                new_rec['break_minutes'] = hr_min2minutes(rec['Leg Time'])
                continue

            waypoint = rec['Waypoint']
            #!print(f"{rec['Waypoint']=} {camp_cnt=} {day=} {travel_day=}")

            match waypoint:
                case 'Start': # Start of segment (line for route or track)
                    eod = False
                    rec.update(normal_rec)
                    if start_latlon is None:
                        start_elevation = int(rec['Elevation'].strip("'"))
                        start_latlon = [float(n)
                                        for n in rec['Coordinates'].split(',')]
                case 'camp' | 'car': # "End" means of seg, this is of Day
                    eod = True
                    camp_cnt += 1
                    travel_day += 1
                case 'End': # End of segment (line for route or track)
                    # Replace "End" with "EOD" but only at end of day
                    # There is always a "total" WP for very segment, but
                    # not quite always an "End" WP!!? If so, tweak in CalTopo.
                    eod_rec = {
                        'day': day,
                        'eod': eod,
                        'segment': seg_name,
                        'waypoint': 'EOD',
                        'trip_leg': f"EOD{day}",
                        'elevation': int(prev['Elevation'].strip("'")),
                        'aeg': 0,
                        'ael': 0,
                        'distance': 0,
                        'duration': 0,
                        'break_minutes':  0,
                        'elapsed': elapsed_minutes,
                        'notes': '',
                    }
                    # Add a record after the last End of a day
                    if eod:
                        records.append(eod_rec)
                    continue
                case 'total': # we do our own total calculations
                    # There is always a "total" WP for very segment, but
                    # not quite always an "End" WP!!?
                    # The "total" row is anomolous and applies to SEGMENT
                    # so ignore.  We will calculate DAY totals ourself.
                    day = travel_day
                    continue
                case _: # Any other waypoint
                    pass

            minutes = hr_min2minutes(rec['Leg Time'])
            elapsed_minutes += minutes

            if new_rec:
                records.append(new_rec)

            if rec['Distance'].endswith(' mi'):
                distance = float(rec['Distance'].strip(" mi"))
            elif rec['Distance'].endswith(' ft'):
                distance = float(rec['Distance'].strip(" ft")) / 5280
            else:
                distance = 0.0
            lat, lon = [float(n) for n in rec['Coordinates'].split(',')]
            if rec['Gain'] == "":
                rec['Gain'] = "+0'"
            if rec['Loss'] == "":
                rec['Loss'] = "-0'"
            trip_leg += 1
            new_rec = {
                'day': day,
                'eod': eod,
                'segment': seg_name,
                'waypoint': rec['Waypoint'],
                'trip_leg': trip_leg,
                'elevation': int(rec['Elevation'].strip("'")),
                'aeg': int(rec['Gain'].strip("'")),
                'ael': int(rec['Loss'].strip("'")),
                'distance': distance,
                'duration': minutes,
                'break_minutes':  0,
                'elapsed': elapsed_minutes,
                'notes': rec['Notes'],
            }
            prev = rec
            # Add a record after the last End of a day
            if waypoint == 'End' and eod:
                records.append(eod_rec)
            # END: for rec in reader
        records.append(new_rec)
        #records.append(eod_rec)

        assert camp_cnt > 1, (
            f'For an overnight trip, you need at least one "camp" '
            f'and one "car" waypoint. (got {camp_cnt=})'
            )


        trip = dict(
            start_latlon=start_latlon, # decimal degrees: (lat,lon)
            start_elevation=start_elevation,  # feet
            elapsed_hours = elapsed_minutes/60,
            )


        df = pd.DataFrame(records)
        # Insert columns
        # Hours is "elapsed hours" which includes schedule breaks
        df['hours'] = (df['duration'] + df['break_minutes'])/ 60
        # pace excludes scheduled break_minutes.
        # Assume scheduled breaks are not "gotta rest now" kind of break.
        df['pace'] = (df['duration'] / (df['distance'] + 1e-6)).astype(int)
        col_types = {'elevation': int,
                     'aeg': int,
                     'ael': int,
                     'distance': float,
                     'duration': int,
                     'elapsed': int,  # total minutes (hike + break)
                     'break_minutes': int,
                     'hours': float,
                     'pace': int,
                     }
        df.astype(col_types)
        #! # Insert rows
        #! total_label = 'Total'
        #! total_row = pd.Series(df.sum(axis=0), name=total_label)
        #! df = pd.concat([df, pd.DataFrame(total_row).T], ignore_index=False)
        #!
        #! # Remove senseless values
        #! df.loc[total_label, 'day'] = pd.NA
        #! df.loc[total_label, 'segment'] = pd.NA
        #! df.loc[total_label, 'waypoint'] = pd.NA
        #! df.loc[total_label, 'leg'] = pd.NA
        #! df.loc[total_label, 'elevation'] = pd.NA

        # df columns:
        #   day, segment, waypoint, trip_leg, elevation, aeg, ael,
        #   distance, duration, break_minutes, elapsed, hours, pace

        # Write all data to Excel file
        if excelfname is None:
            excelfname = Path(csvfname).with_suffix('.xlsx')
        with pd.ExcelWriter(Path(excelfname).expanduser()) as writer:
            df.to_excel(writer, sheet_name='Waypoints', index=False)
            pd.DataFrame(trip).T.to_excel(writer,
                                          sheet_name='Meta', index=False)
        print(f'Wrote Excel version of dataframe to {excelfname}')
        return df, trip
