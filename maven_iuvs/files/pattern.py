# Local imports
from maven_iuvs.files.orbit_block import OrbitBlock


class PatternGlob(OrbitBlock):
    """ A PatternGlob object creates glob search patterns tailored to IUVS
    data. """
    def pattern(self, orbit, segment, channel, extension='fits'):
        """ Make a glob pattern for an orbit, segment, and channel.

        Parameters
        ----------
        orbit: str or int
            The orbit to get data from. Can be '*' to get all orbits.
        segment: str or int
            The segment to get data from. Can be '*' to get all segments.
        channel: str or int
            The channel to get data from. Can be '*' to get all channels.
        extension: str
            The file extension to use. Default is 'fits'

        Returns
        -------
        pattern: str
            The glob pattern that matches the input parameters.
        """
        if orbit == '*':
            pattern = f'*{segment}-*-{channel}*.{extension}*'
        else:
            pattern = f'*{segment}-*{self._orbit_to_string(orbit)}-' \
                      f'{channel}*.{extension}*'
        return self.__remove_recursive_glob_pattern(pattern)

    def recursive_pattern(self, orbit, segment, channel):
        """ Make a recursive glob pattern for an orbit, segment, and channel.

        Parameters
        ----------
        orbit: str or int
            The orbit to get data from. Can be '*' to get all orbits.
        segment: str or int
            The segment to get data from. Can be '*' to get all segments.
        channel: str or int
            The channel to get data from. Can be '*' to get all channels.

        Returns
        -------
        pattern: str
            The recursive glob pattern that matches the input parameters.
        """
        pattern = self.pattern(orbit, segment, channel)
        return self.__prepend_recursive_glob_pattern(pattern)

    def orbit_patterns(self, orbits, segment, channel):
        """ Make glob patterns for each orbit in a list of orbits.

        Parameters
        ----------
        orbits: list
            List of ints or strings of orbits to make patterns for.
        segment: str or int
            The segment to get data from. Can be '*' to get all segments.
        channel: str or int
            The channel to get data from. Can be '*' to get all channels.

        Returns
        -------
        patterns: list
            List of patterns of len(orbits) that match the inputs.
        """
        orbs = [self._orbit_to_string(orbit) for orbit in orbits]
        return [self.pattern(orbit, segment, channel) for orbit in orbs]

    def recursive_orbit_patterns(self, orbits, sequence, channel):
        """ Make recursive glob patterns for each orbit in a list of orbits.

        Parameters
        ----------
        orbits: list
            List of ints or strings of orbits to make patterns for.
        sequence: str or int
            The sequence to get data from. Can be '*' to get all sequences.
        channel: str or int
            The channel to get data from. Can be '*' to get all channels.

        Returns
        -------
        patterns: list
            List of recursive patterns of len(orbits) that match the inputs.
        """
        return [self.__prepend_recursive_glob_pattern(f) for f in
                self.orbit_patterns(orbits, sequence, channel)]

    @staticmethod
    def __remove_recursive_glob_pattern(pattern):
        return pattern.replace('**', '*')

    @staticmethod
    def __prepend_recursive_glob_pattern(pattern):
        return f'**/{pattern}'
