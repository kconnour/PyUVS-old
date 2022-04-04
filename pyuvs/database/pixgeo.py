import psycopg
from pyuvs.datafiles import L1bFile, find_latest_apoapse_muv_file_paths_from_block, L1bFileCollection
from pathlib import Path

pixid = 10076612
intid = 75764
for i in range(3430, 3500):
    p = Path('/media/kyle/Samsung_T5/IUVS_data')
    allfiles = find_latest_apoapse_muv_file_paths_from_block(p, i)
    files = [L1bFile(f) for f in allfiles]
    # fc = L1bFileCollection(files)
    # print(fc.stack_field_of_view().shape)

    with psycopg.connect(host='localhost', dbname='iuvs', user='kyle', password='iuvs') as connection:
        with connection.cursor() as cursor:
            '''cursor.execute("""create table public.pixel (
            pixelID serial constraint pixel_pk primary key,
            integrationID integer not null,
            spatial_bin integer not null)
            """)
    
            cursor.execute("""create table public.integration (
            integrationID serial constraint integration_pk primary key,
            n_spatial_bins integer not null,
            orbit integer not null)
            """)
    
            cursor.execute("""create table pixelgeometry.latitude (
            pixelID serial constraint latitude_pk primary key,
            lower_left double precision not null,
            upper_left double precision not null,
            lower_right double precision not null,
            upper_right double precision not null,
            center double precision not null)
            """)
            cursor.execute("""create table pixelgeometry.longitude (
            pixelID serial constraint longitude_pk primary key,
            lower_left double precision not null,
            upper_left double precision not null,
            lower_right double precision not null,
            upper_right double precision not null,
            center double precision not null)
            """)
            cursor.execute("""create table pixelgeometry.tangent_altitude (
            pixelID serial constraint altitude_pk primary key,
            lower_left double precision not null,
            upper_left double precision not null,
            lower_right double precision not null,
            upper_right double precision not null,
            center double precision not null)
            """)
            cursor.execute("""create table pixelgeometry.solar_zenith_angle (
            pixelID serial constraint solar_zenith_angle_pk primary key,
            center double precision not null)
            """)
            cursor.execute("""create table pixelgeometry.emission_angle (
            pixelID serial constraint emission_angle_pk primary key,
            center double precision not null)
            """)
            cursor.execute("""create table pixelgeometry.phase_angle (
            pixelID serial constraint phase_angle_pk primary key,
            center double precision not null)
            """)'''

            for counter, file in enumerate(files):
                for integration in range(file.pixel_geometry.latitude.shape[0]):
                    for position in range(file.pixel_geometry.latitude.shape[1]):
                        print(f'starting orbit {i}, integration {integration}, position {position}.')
                        cursor.execute(f'insert into public.pixel (pixelID, integrationid, spatial_bin) values ({pixid}, {integration}, {position})')
                        lat = file.pixel_geometry.latitude
                        lon = file.pixel_geometry.longitude
                        alt = file.pixel_geometry.tangent_altitude
                        sza = file.pixel_geometry.solar_zenith_angle
                        ea = file.pixel_geometry.emission_angle
                        pa = file.pixel_geometry.phase_angle
                        if position == 0:
                            cursor.execute(f'insert into public.integration (integrationID, n_spatial_bins, orbit) values ({intid}, {lat.shape[1]}, {i})')
                        cursor.execute(
                            f'insert into pixelgeometry.latitude (pixelID, lower_left, upper_left, lower_right, upper_right, center) '
                            f'values ({pixid}, {lat[integration, position, 0]}, '
                            f'{lat[integration, position, 1]}, '
                            f'{lat[integration, position, 2]}, '
                            f'{lat[integration, position, 3]}, '
                            f'{lat[integration, position, 4]})')
                        cursor.execute(
                            f'insert into pixelgeometry.longitude (pixelID, lower_left, upper_left, lower_right, upper_right, center) '
                            f'values ({pixid}, {lon[integration, position, 0]}, '
                            f'{lon[integration, position, 1]}, '
                            f'{lon[integration, position, 2]}, '
                            f'{lon[integration, position, 3]}, '
                            f'{lon[integration, position, 4]})')
                        cursor.execute(
                            f'insert into pixelgeometry.tangent_altitude (pixelID, lower_left, upper_left, lower_right, upper_right, center) '
                            f'values ({pixid}, {alt[integration, position, 0]}, '
                            f'{alt[integration, position, 1]}, '
                            f'{alt[integration, position, 2]}, '
                            f'{alt[integration, position, 3]}, '
                            f'{alt[integration, position, 4]})')
                        cursor.execute(
                            f'insert into pixelgeometry.solar_zenith_angle (pixelID, center) '
                            f'values ({pixid}, {sza[integration, position]})')
                        cursor.execute(
                            f'insert into pixelgeometry.emission_angle (pixelID, center) '
                            f'values ({pixid}, {ea[integration, position]})')
                        cursor.execute(
                            f'insert into pixelgeometry.phase_angle (pixelID, center) '
                            f'values ({pixid}, {pa[integration, position]})')
                        pixid += 1
                    intid += 1
