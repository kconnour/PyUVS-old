import pickle

with open('/home/kyle/myOrbitDict.pickle', 'rb') as handle:
    foo = pickle.load(handle)

print(foo['orbit_numbers'][-1])
print(foo['subsc_lat'][3999, 2])
print(foo['subsc_alt_km'][3999, 2])
print(foo['solar_longitude'][3999, 2])
