import psycopg
from pathlib import Path
from pyuvs.spice import Spice, PositionFinder

apse = 'apoapse'
with psycopg.connect(host='localhost', dbname='iuvs', user='kyle', password='iuvs') as connection:
    # I still need Mars year, Sol
    # Open a cursor for db operations
    with connection.cursor() as cursor:
        cursor.execute(f"""create table {apse} (
        orbit serial constraint {apse}_pk primary key,
        ephemeris_time double precision not null,
        mars_year integer not null,
        sol double precision not null,
        solar_longitude double precision not null,
        utc timestamptz not null,
        subspacecraft_latitude double precision not null,
        subspacecraft_longitude double precision not null,
        subspacecraft_altitude double precision not null,
        solar_distance double precision not null,
        subsolar_latitude double precision not null,
        subsolar_longitude double precision not null)
        
        """)

        cursor.execute(f"""
        create unique index {apse}_orbit_uindex on {apse} (orbit);""")


if __name__ == '__main__':
    import time
    from datetime import datetime
    import mer
    p = Path('/media/kyle/McDataFace/spice')
    t0 = time.time()
    s = Spice(p)
    s.load_spice()
    t1 = time.time()
    orbits, all_et = s.find_all_maven_apsis_et('apoapse', endtime=datetime(2022, 5, 29))

    print('found apsis info')

    for orbit in orbits:
        et = all_et[orbits==orbit][0]
        pf = PositionFinder(et)
        ls = pf.get_ls()
        sc_lat, sc_lon = pf.get_subspacecraft_point()
        sol_lat, sol_lon = pf.get_subsolar_point()
        sc_alt = pf.get_subspacecraft_altitude()
        dist = pf.get_mars_sun_distance()
        dt = pf.get_datetime()
        isoformat = '%Y-%m-%d %H:%M:%S.%f%z'
        # return the datetime object version of the input ephemeris time
        ft = datetime.strftime(dt, isoformat)
        ft = f"'{ft}'"
        edt = mer.EarthDateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)
        my = edt.to_whole_mars_year()
        sol = edt.to_sol()
        print(f'made info for orbit {orbit}')
        with psycopg.connect(host='localhost', dbname='iuvs', user='kyle',
                             password='iuvs') as connection:
            # Open a cursor for db operations
            with connection.cursor() as cursor:
                cursor.execute(f'insert into apoapse (orbit, ephemeris_time, '
                               f'mars_year, sol, solar_longitude, utc, '
                               f'subspacecraft_latitude, subspacecraft_longitude, '
                               f'subspacecraft_altitude, solar_distance, '
                               f'subsolar_latitude, subsolar_longitude) '
                               f'values ({orbit}, {et}, {my}, {sol}, {ls}, {ft}, {sc_lat}, {sc_lon}, {sc_alt}, {dist}, {sol_lat}, {sol_lon})'
                )
