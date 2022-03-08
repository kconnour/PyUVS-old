import psycopg
import numpy as np
import matplotlib.pyplot as plt


with psycopg.connect(host='localhost', dbname='iuvs', user='kyle', password='iuvs') as connection:
    # I still need Mars year, Sol
    # Open a cursor for db operations
    with connection.cursor() as cursor:
        cursor.execute("""select orbit from apoapse;""")
        orbs = np.squeeze(np.array(cursor.fetchall()))
        cursor.execute("""select subspacecraft_latitude from apoapse;""")
        alts = np.squeeze(np.array(cursor.fetchall()))

        plt.plot(orbs, alts)

        plt.savefig('/home/kyle/scalt.png')

