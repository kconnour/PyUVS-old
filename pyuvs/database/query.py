import psycopg

with psycopg.connect(host='localhost', dbname='iuvs', user='kyle', password='iuvs') as connection:
    # I still need Mars year, Sol
    # Open a cursor for db operations
    with connection.cursor() as cursor:
        cursor.execute("select solar_distance from apoapse where orbit = 3400")
        #cursor.execute("select utc from apoapse where orbit = 1")
        a = cursor.fetchall()

#dt = a[0][0].month
#print(dt)
a = a[0][0]

rearth = 1.496e8
print(a/rearth)
