import datetime as dt
from zoneinfo import ZoneInfo
import warnings

import astropy.coordinates
import pandas as pd
import pytz  # DEPRECATED in favor of zoneinfo
import zoneinfo
from astroplan import Observer
from astropy.time import Time
from astropy import units as u


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

geodetic_coords = {
    'Manua Kea': {
        'lat': 19.82333,
        'lon': -155.46833,
        'elevation': 4214,  # meters
        'tzkey': 'HST'
        },
    'tucson': {
        'lat': 32.30942,
        'lon': -110.82205,
        'elevation': 831,  # meters
        'tzkey': 'America/Phoenix',
        },
    }

# alm_gn = Almanac(**gtp.geodetic_coords['gemini_north'])
class Almanac():
    """Get almanac data for a night given a date.
    A dayobs is the date of the start of an observing night. Therefore
    for sunrise and morning twilight we get time on the date AFTER dayobs.
    For sunset and evening twilight we get time on date of dayobs.
    For moonrise/set we get the time nearest to the midnight after day_ob.
    All times are in UTC.  Convert afterwards if needed.
    For list of timeszones: pytz.all_timezones
    E.G. [s for s in pytz.all_timezones if 'HST' in s]
         [s for s in pytz.all_timezones if 'Chile' in s]

    To get list of site_names:
       astropy.coordinates.EarthLocation.get_site_names()
    Compare Gemini_South to
       https://www.timeanddate.com/astronomy/@-30.23946,-70.73954
    Compare Gemini_North to
       https://www.timeanddate.com/astronomy/@19.82438,-155.46916
    """

    def __init__(
        self,
        lat: float,
        lon: float,
        tzkey: str,
        elevation: float = 0.0, # meters
        date: int | None = None, # YYYYMMDD
        #!timezone: dt.timedelta,  # UTC offset
        # default to night ending TODAY
        #!dayobs: int | None = None,  # YYYYMMDD
        # site="gemini_north", # gemini_north | gemini_south
    ):
        self.tzinfo = ZoneInfo(tzkey)

        if date is None:
            date = int(str(dt.date.today()).replace('-',''))

        #! else:
        #!     dobs = str(dayobs)
        #! dome_tz = pytz.timezone(timezone)
        #! self.dome_noon = Time(
        #!     dome_tz.localize(dt.datetime.strptime(dobs + " 12:00", "%Y%m%d %H:%M"))
        #! )

        #!astro_day = dt.datetime.strptime(dobs, "%Y%m%d").date()
        #!astro_date = dt.datetime.strptime(dobs, "%Y%m%d")
        self.date = date
        # Midnight is ambigious wrt date. Use just before midnight for clarity.
        # We use this to get the NEAREST sunrise/sunset etc
        # (which are different local days)
        self.dt_pre_midnight = dt.datetime.combine(
            dt.datetime.strptime(str(date),'%Y%m%d').date(),
            dt.time(23,59,59),
            tzinfo=self.tzinfo)
        self.pre_midnight = Time(
            self.dt_pre_midnight,
            format="datetime",
            scale="utc"
        )


        with warnings.catch_warnings(action="ignore"):
            #!self.loc = astropy.coordinates.EarthLocation.of_site(site)
            #! self.loc = astropy.coordinates.EarthLocation.from_geodetic(
            #!     lon,
            #!     lat,
            #!     height=elevation
            #!     )
            #!self.observer = Observer(self.loc, timezone=timezone)
            self.observer = Observer(latitude=lat * u.deg,
                                     longitude=lon * u.deg,
                                     elevation=elevation * u.m,
                                     timezone=tzkey)
            #! self.astro_day = astro_day
            #! self.astro_midnight = self.observer.midnight(
            #!     Time(
            #!         astro_date,
            #!         format="datetime",
            #!         scale="utc",
            #!     ),
            #!     which="next",
            #! )
            self.get_moon()
            self.get_sun()


    def __repr__(self):
        return (
            f'{self.date=} '
            f'{self.observer} '
            #!f'{self.tzinfo=} '
            f'pre-midnight(UTC)='
            f'{str(self.pre_midnight.to_datetime(timezone=ZoneInfo("UTC")))} '
            )

    def get_moon(self):
        self.moon_rise_time = self.observer.moon_rise_time(
            self.pre_midnight, which="nearest"
        )
        self.moon_set_time = self.observer.moon_set_time(
            self.pre_midnight, which="nearest"
        )

        # Percent of moon lit
        self.moon_illum = self.observer.moon_illumination(self.pre_midnight)

    def get_sun(self):
        # ast(ronoimical) twilight: -18 degrees)
        obs = self.observer
        self.ast_twilight_morning = obs.twilight_morning_astronomical(
            self.pre_midnight, which="nearest"
        )
        self.ast_twilight_evening = obs.twilight_evening_astronomical(
            self.pre_midnight, which="nearest"
        )

        # nau(tical) twilight: -12 degrees)
        self.nau_twilight_morning = self.observer.twilight_morning_nautical(
            self.pre_midnight, which="nearest"
        )
        self.nau_twilight_evening = self.observer.twilight_evening_nautical(
            self.pre_midnight, which="nearest"
        )

        # civ(il) twilight: -6 degrees)
        self.civ_twilight_morning = self.observer.twilight_morning_civil(
            self.pre_midnight, which="nearest"
        )
        self.civ_twilight_evening = self.observer.twilight_evening_civil(
            self.pre_midnight, which="nearest"
        )

        self.sun_rise_time = self.observer.sun_rise_time(
            self.pre_midnight, which="nearest"
        )
        self.sun_set_time = self.observer.sun_set_time(
            self.pre_midnight, which="nearest"
        )

    @property
    def night_hours(self):
        day_delta = self.ast_twilight_morning - self.ast_twilight_evening
        return day_delta.to_value("hr")

    @property
    def night_time(self):
        """(nightStartDatetime, nightEndDatetime) using 18deg twilight"""
        # set,rise
        return (self.events()['sunset_18deg'], self.events()['sunrise_18deg'])

    def events(self, iso=False, tzkey=None):
        """Sun/Moon datetime in UTC. Use localize=True for Chile time."""
        events = dict(  # as astropy.Time
            moon_rise=self.moon_rise_time,
            moon_set=self.moon_set_time,
            sunrise_18deg=self.ast_twilight_morning,
            sunset_18deg=self.ast_twilight_evening,
            sunrise_12deg=self.nau_twilight_morning,
            sunset_12deg=self.nau_twilight_evening,
            sunrise_6deg=self.civ_twilight_morning,
            sunset_6deg=self.civ_twilight_evening,
            sunrise=self.sun_rise_time,
            sunset=self.sun_set_time,
        )

        if tzkey is None:
            events_dt = {
                k: self.observer.astropy_time_to_datetime(v)
                for k, v in events.items()
            }
        else:
            tz = ZoneInfo(tzkey)
            events_dt = {
                k: self.observer.astropy_time_to_datetime(v).astimezone(tz)
                for k, v in events.items()
            }

        if iso:
            return {
                k: v.isoformat(sep=" ", timespec="seconds")
                for k, v in events_dt.items()
            }
        else:
            return events_dt

    @property
    def dataframe(self):
        df = pd.DataFrame(
            [
                #!self.events(localize=True, iso=True),
                self.events(localize=False, iso=True),
            ]
        ).T
        df.columns = ["UTC"]
        df.index.name = "Event"
        return df.sort_values(by="UTC").reset_index().set_index("UTC")

    @property
    def as_dict(self):
        moon_rise_time = Time(self.moon_rise_time, precision=0).iso
        moon_set_time = Time(self.moon_set_time, precision=0).iso
        ast_twilight_morning = Time(self.ast_twilight_morning, precision=0).iso
        ast_twilight_evening = Time(self.ast_twilight_evening, precision=0).iso
        nau_twilight_morning = Time(self.nau_twilight_morning, precision=0).iso
        nau_twilight_evening = Time(self.nau_twilight_evening, precision=0).iso
        civ_twilight_morning = Time(self.civ_twilight_morning, precision=0).iso
        civ_twilight_evening = Time(self.civ_twilight_evening, precision=0).iso
        sun_rise_time = Time(self.sun_rise_time, precision=0).iso
        sun_set_time = Time(self.sun_set_time, precision=0).iso

        # Maybe it we should add a column of times for the Dome.
        # It would make it easier to do some kinds of sanity checks.
        # Then again, it might confuse the issues.
        # It depends on who will be looking this the most.
        # Observers in the Dome? People elsewhere?

        data_dict = {
            "": "UTC",
            "Moon Rise": moon_rise_time,
            "Moon Set": moon_set_time,
            "Moon Illumination": f"{self.moon_illum:.0%}",
            "Morning Astronomical Twilight": ast_twilight_morning,
            "Evening Astronomical Twilight": ast_twilight_evening,
            "Morning Nautical Twilight": nau_twilight_morning,
            "Evening Nautical Twilight": nau_twilight_evening,
            "Morning Civil Twilight": civ_twilight_morning,
            "Evening Civil Twilight": civ_twilight_evening,
            "Sun Rise": sun_rise_time,
            "Sun Set": sun_set_time,
        }
        help_dict = {
            "": "",
            "Moon Set": "",
            "Moon Rise": "",
            "Moon Illumination": "(% illuminated)",
            "Morning Astronomical Twilight": "(-18 degrees)",
            "Evening Astronomical Twilight": "(-18 degrees)",
            "Solar Midnight": "",
            "Morning Nautical Twilight": "(-12 degrees)",
            "Evening Nautical Twilight": "(-12 degrees)",
            "Morning Civil Twilight": "(-6 degrees)",
            "Evening Civil Twilight": "(-6 degrees)",
            "Sun Set": "",
            "Sun Rise": "",
        }
        return data_dict, help_dict

    # A time_log is a DF ordered and indexed with DatetimeIndex.
    def as_records(self):
        """Sun/Moon events indexed by UTC (ISO string truncated to seconds)"""
        return self.dataframe.reset_index().to_dict(orient="records")
