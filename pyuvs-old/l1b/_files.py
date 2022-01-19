from pyuvs.files import DataFilenameCollection


class L1bDataFilenameCollection:
    def __init__(self, files: DataFilenameCollection):
        self.__files = files

    def __raise_value_error_if_not_all_l1b(self) -> None:
        if not self.__files.all_l1b():
            message = 'Some files are not all level 1b.'
            raise ValueError(message)
