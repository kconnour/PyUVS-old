# TODO: Most of the logic here could go into a higher class like IUVSFilename
#  so that it could work on .xml files or quicklooks


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
        self.__check_input_is_iuvs_data_filename()

    def __str__(self):
        return self.__filename

    def __check_input_is_iuvs_data_filename(self):
        self.__check_spacecraft_is_mvn()
        self.__check_instrument_is_iuv()
        self.__check_filename_has_fits_extension()
        self.__check_filename_contains_6_underscores()
        self.__check_filename_contains_orbit()

    def __check_spacecraft_is_mvn(self):
        if not self.spacecraft == 'mvn':
            raise ValueError('The input file is not an IUVS data file.')

    def __check_instrument_is_iuv(self):
        if not self.instrument == 'iuv':
            raise ValueError('The input file is not an IUVS data file.')

    def __check_filename_has_fits_extension(self):
        if 'fits' not in self.extension:
            raise ValueError('The input file is not an IUVS data file.')

    def __check_filename_contains_6_underscores(self):
        if self.filename.count('_') != 6:
            raise ValueError('The input file is not an IUVS data file.')

    def __check_filename_contains_orbit(self):
        if 'orbit' not in self.filename:
            raise ValueError('The input file is not an IUVS data file.')

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
