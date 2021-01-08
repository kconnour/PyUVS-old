

class IUVSDataFilename:
    """ And IUVSDataFilename object contains methods to extract info from a
    filename of an IUVS data product. """
    def __init__(self, filename):
        """
        Parameters
        ----------
        filename: str
            The IUVS data filename.
        """
        self.__filename = filename

    # TODO: check input is an IUVS filename. I shouldn't be able to make a class of a non-IUVS filename

    @property
    def filename(self):
        """ Get the input filename.

        Returns
        -------
        filename: str
            The input filename.
        """
        return self.__filename

    @property
    def spacecraft(self):
        """ Get the spacecraft code from the filename.

        Returns
        -------
        spacecraft: str
            The spacecraft code.
        """
        return self.__split_filename()[0]

    @property
    def instrument(self):
        """ Get the instrument code from the filename.

        Returns
        -------
        instrument: str
            The instrument code.
        """
        return self.__split_filename()[1]

    @property
    def level(self):
        """ Get the data product level from the filename.

        Returns
        -------
        level: str
            The data product level.
        """
        return self.__split_filename()[2]

    @property
    def observation(self):
        """ Get the observation ID from the filename.

        Returns
        -------
        observation: str
            The observation ID.
        """
        return self.__split_filename()[3]

    @property
    def segment(self):
        """ Get the observation segment from the filename.

        Returns
        -------
        segment: str
            The observation segment.
        """
        if len(splits := self.__split_observation()) == 3:
            return splits[0]
        else:
            return splits[0] + '-' + splits[1]

    @property
    def orbit(self):
        """ Get the orbit number from the filename.

        Returns
        -------
        orbit: int
            The orbit number.
        """
        return int(self.__split_observation()[-2].removeprefix('orbit'))

    @property
    def channel(self):
        """ Get the observation channel from the filename.

        Returns
        -------
        channel: str
            The observation channel.
        """
        return self.__split_observation()[-1]

    @property
    def timestamp(self):
        """ Get the timestamp of the observation from the filename.

        Returns
        -------
        timestamp: str
            The timestamp of the observation.
        """
        return self.__split_filename()[4]

    @property
    def date(self):
        """ Get the date of the observation from the filename.

        Returns
        -------
        date: str
            The date of the observation.
        """
        return self.__split_timestamp()[0]

    @property
    def year(self):
        """ Get the year of the observation from the filename.

        Returns
        -------
        year: int
            The year of the observation.
        """
        return int(self.date[:4])

    @property
    def month(self):
        """ Get the month of the observation from the filename.

        Returns
        -------
        month: int
            The month of the observation.
        """
        return int(self.date[4:6])

    @property
    def day(self):
        """ Get the day of the observation from the filename.

        Returns
        -------
        day: int
            The day of the observation.
        """
        return int(self.date[6:])

    @property
    def time(self):
        """ Get the time of the observation from the filename.

        Returns
        -------
        time: str
            The time of the observation.
        """
        return self.__split_timestamp()[1]

    @property
    def hour(self):
        """ Get the hour of the observation from the filename.

        Returns
        -------
        hour: int
            The hour of the observation.
        """
        return int(self.time[:2])

    @property
    def minute(self):
        """ Get the minute of the observation from the filename.

        Returns
        -------
        minute: int
            The minute of the observation.
        """
        return int(self.time[2:4])

    @property
    def second(self):
        """ Get the second of the observation from the filename.

        Returns
        -------
        second: int
            The second of the observation.
        """
        return int(self.time[4:])

    @property
    def version(self):
        """ Get the version code from the filename.

        Returns
        -------
        version: str
            The version code.
        """
        return self.__split_filename()[5]

    @property
    def revision(self):
        """ Get the revision code from the filename.

        Returns
        -------
        revision: str
            The revision code.
        """
        return self.__split_filename()[6]

    @property
    def extension(self):
        """ Get the extension of filename.

        Returns
        -------
        extension: str
            The extension.
        """
        return self.__split_stem_from_extension()[1]

    def __split_stem_from_extension(self):
        extension_index = self.filename.find('.')
        stem = self.filename[:extension_index]
        extension = self.filename[extension_index + 1:]
        return [stem, extension]

    def __split_filename(self):
        stem = self.__split_stem_from_extension()[0]
        return stem.split('_')

    def __split_timestamp(self):
        return self.timestamp.split('T')

    def __split_observation(self):
        return self.observation.split('-')


test = 'mvn_iuv_l1b_relay-echelle-orbit12201-ech_20200823T121455_v13_r01.fits.gz'
t1 = 'mvn_iuv_l1b_periapse-orbit03453-muv_20160708T031729_v13_r01.fits.gz'
f = IUVSDataFilename(test)
