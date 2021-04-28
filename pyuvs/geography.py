"""The geography module contains classes to compute geographic information.
"""
import numpy as np


class Geography:
    def __init__(self):
        self.r_mars = 3390
        self.locations = self.__make_locations()

    @staticmethod
    def __make_locations() -> dict:
        locations = {'gale_crater': (-5.24, 127.48)}
        return locations

    def closest_pixel(self, contents,
                      location: tuple, threshhold: float = 15) -> tuple:
        lats = contents.latitude[:, :, 4]
        lons = contents.longitude[:, :, 4]
        distances = self.haversine_distance(
            lats, lons, location[0], location[1])
        closest_distance = np.amin(distances)

        if closest_distance < threshhold:
            closest_distance_ind = np.where(np.amin(distances) == distances)
            position_index = closest_distance_ind[0][0]
            integration_index = closest_distance_ind[1][0]
        else:
            position_index = None
            integration_index = None

        return position_index, integration_index

    def location_in_file(self, contents: L1bDataContents,
                         location: tuple, threshhold: float = 15) -> bool:
        return True if self.closest_pixel(contents, location,
                                          threshhold=threshhold) != (None, None) \
            else False

    # This should be named better
    def haversine_distance(self, latitudes: np.ndarray, longitudes: np.ndarray,
                           target_lat: float, target_lon: float):
        """Compute the distance [km] between a target point and an array of
        points

        Parameters
        ----------
        latitudes
        longitudes
        target_lat
        target_lon

        Returns
        -------

        """
        a = self.__haversine(latitudes, longitudes, target_lat, target_lon)
        return 2 * self.r_mars * np.arcsin(np.sqrt(a))

    # This should be named better
    def haversine_angle(self, latitudes: np.ndarray, longitudes: np.ndarray,
                        target_lat: float, target_lon: float):
        """Compute the distance [degrees] between a target point and an array of
        points

        Parameters
        ----------
        latitudes
        longitudes
        target_lat
        target_lon

        Returns
        -------

        """
        a = self.__haversine(latitudes, longitudes, target_lat, target_lon)
        return np.degrees(2 * np.arcsin(np.sqrt(a)))

    # I'm not really sure if this is the best name...
    def __haversine(self, latitudes: np.ndarray, longitudes: np.ndarray,
                  target_lat: float, target_lon: float) -> np.ndarray:
        d_lat = np.radians(latitudes - target_lat)
        d_lon = np.radians(longitudes - target_lon)

        # Turn that angular distance into a physical distance
        a = np.sin(d_lat / 2) ** 2 + np.cos(np.radians(target_lat)) * np.cos(
            np.radians(latitudes)) * np.sin(d_lon / 2) ** 2
        return a


    '''def find_closest_location(files, coordinates, threshhold=25, best_scan=False):
        """
    
        Parameters
        ----------
        files
        coordinates
        threshhold
        best_scan
    
        Returns
        -------
    
        """
        for scan, file in enumerate(files):
            # Get all the pixel center latitudes and longitudes from each file
            hdulist = fits.open(file)
            latitudes = hdulist['pixelgeometry'].data['pixel_corner_lat'][:, :, 4]
            longitudes = hdulist['pixelgeometry'].data['pixel_corner_lon'][:, :, 4]
    
            # Find the distances between these points and the target point
            distances = haversine(coordinates[0], coordinates[1], latitudes, longitudes)
            closest_distance = np.amin(distances)
            if closest_distance < threshhold:
                closest_distance_ind = np.where(np.amin(distances) == distances)
                threshhold = closest_distance
                best_scan = scan
    
        if not best_scan:
            print('The requested feature is not in this orbit')
            return
        else:
            return best_scan, closest_distance_ind[0][0], closest_distance_ind[1][0], threshhold
    
    
    def find_location(orbit, data_location, feature):
        """
    
        Parameters
        ----------
        orbit
        data_location
        feature
    
        Returns
        -------
    
        Examples
        -------
        >>> find_location(3453, '/media/kyle/Samsung_T5/IUVS_data/', 'arsia')
        (8, 32, 2, 0.8211884454454046)
        >>> find_location(3453, '/media/kyle/Samsung_T5/IUVS_data/', 'north_pole')
        That location is not a known location. Add it to the dictionary to continue
        >>> find_location(3455, '/media/kyle/Samsung_T5/IUVS_data/', 'arsia')
        The requested feature is not in this orbit
        """
        files = filter_files(orbit, data_location)
    
        coordinates = check_location(feature, make_location_dict())
        best_scan, best_position, best_integration, closest_distance = find_closest_location(files, coordinates)
        return best_scan, best_position, best_integration, closest_distance'''
