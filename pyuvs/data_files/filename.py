from pathlib import Path


class DataFilename:
    """A data structure containing info from a single IUVS filename.

    It ensures the input filename represents an IUVS filename and extracts all
    information related to the observation and processing pipeline from the
    input.

    Parameters
    ----------
    path
        The absolute path of an IUVS data product.

    Raises
    ------
    FileNotFoundError
        Raised if the input path does not lead to a valid file.
    TypeError
        Raised if the input path is not a string.
    ValueError
        Raised if the file is not an IUVS data file.

    """
    def __init__(self, path: str) -> None:
        self._path = self.__create_path(path)
        self._filename = self._path.name

    @staticmethod
    def __create_path(path: str) -> Path:
        return Path(path)

    def __str__(self) -> str:
        return str(self._path)

    @property
    def path(self) -> str:
        """Get the input absolute path.

        """
        return str(self._path)

    @property
    def filename(self) -> str:
        """Get the filename from the absolute path.

        """
        return self._filename

    @property
    def spacecraft(self) -> str:
        """Get the spacecraft code from the filename.

        """
        return self.__split_filename_on_underscore()[0]

    @property
    def instrument(self) -> str:
        """Get the instrument code from the filename.

        """
        return self.__split_filename_on_underscore()[1]

    @property
    def level(self) -> str:
        """Get the data product level from the filename.

        """
        return self.__split_filename_on_underscore()[2]

    @property
    def description(self) -> str:
        """Get the description from the filename.

        """
        return self.__split_filename_on_underscore()[3]

    @property
    def segment(self) -> str:
        """Get the observation segment from the filename.

        """
        orbit_index = self.__get_split_index_containing_orbit()
        segments = self.__split_description()[:orbit_index]
        return '-'.join(segments)

    @property
    def orbit(self) -> int:
        """Get the orbit number from the filename.

        """
        orbit_index = self.__get_split_index_containing_orbit()
        orbit = self.__split_description()[orbit_index].removeprefix('orbit')
        return int(orbit)

    @property
    def channel(self) -> str:
        """Get the observation channel from the filename.

        """
        orbit_index = self.__get_split_index_containing_orbit()
        try:
            return self.__split_description()[orbit_index + 1]
        except IndexError:
            return None

    @property
    def timestamp(self) -> str:
        """Get the timestamp of the observation from the filename.

        """
        return self.__split_filename_on_underscore()[4]

    @property
    def date(self) -> str:
        """Get the date of the observation from the filename.

        """
        return self.__split_timestamp()[0]

    @property
    def year(self) -> int:
        """Get the year of the observation from the filename.

        """
        return int(self.date[:4])

    @property
    def month(self) -> int:
        """Get the month of the observation from the filename.

        """
        return int(self.date[4:6])

    @property
    def day(self) -> int:
        """Get the day of the observation from the filename.

        """
        return int(self.date[6:])

    @property
    def time(self) -> str:
        """Get the time of the observation from the filename.

        """
        return self.__split_timestamp()[1]

    @property
    def hour(self) -> int:
        """Get the hour of the observation from the filename.

        """
        return int(self.time[:2])

    @property
    def minute(self) -> int:
        """Get the minute of the observation from the filename.

        """
        return int(self.time[2:4])

    @property
    def second(self) -> int:
        """Get the second of the observation from the filename.

        """
        return int(self.time[4:])

    @property
    def version(self) -> str:
        """Get the version code from the filename.

        """
        return self.__split_filename_on_underscore()[5]

    @property
    def revision(self) -> str:
        """Get the revision code from the filename.

        """
        return self.__split_filename_on_underscore()[6]

    @property
    def extension(self) -> str:
        """Get the extension of filename.

        """
        return self.__split_stem_from_extension()[1]

    def __split_filename_on_underscore(self) -> list[str]:
        stem = self.__split_stem_from_extension()[0]
        return stem.split('_')

    def __split_stem_from_extension(self) -> list[str]:
        extension_index = self._filename.find('.')
        stem = self._filename[:extension_index]
        extension = self._filename[extension_index + 1:]
        return [stem, extension]

    def __split_timestamp(self) -> list[str]:
        return self.timestamp.split('T')

    def __split_description(self) -> list[str]:
        return self.description.split('-')

    def __get_split_index_containing_orbit(self) -> int:
        return [c for c, f in enumerate(self.__split_description())
                if 'orbit' in f][0]
