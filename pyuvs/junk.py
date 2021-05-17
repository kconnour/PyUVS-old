from pathlib import Path


class IUVSDataPath:
    def __init__(self, path: str) -> None:
        self.__path = self.__make_path(path)

        self.__raise_file_not_found_error_if_file_does_not_exist()
        self.__raise_file_exists_error_if_not_iuvs_file()

    @staticmethod
    def __make_path(path: str) -> Path:
        try:
            return Path(path)
        except TypeError:
            message = f'path should be a str, not a {type(path)}.'
            raise TypeError(message)

    def __raise_file_not_found_error_if_file_does_not_exist(self) -> None:
        if not self.__path.exists():
            message = 'The input path does not exist.'
            raise FileNotFoundError(message)

    def __raise_file_exists_error_if_not_iuvs_file(self) -> None:
        if not self.__path.name.startswith('mvn_iuv_'):
            raise FileExistsError('The input file is not an IUVS file.')



    '''

    def __extract_filename_from_path(self) -> str:
        try:
            return os.path.basename(self.__path)
        except TypeError as te:
            raise TypeError('Cannot get the basename from the path.') from te

    def __raise_file_exists_error_if_not_iuvs_file(self) -> None:
        if not self.__filename.startswith('mvn_iuv_'):
            raise FileExistsError('The input file is not an IUVS file.')'''


if __name__ == '__main__':
    i = IUVSDataPath('/home/kyle/mvn_iuv_ql_apoapse-orbit03453-muv-TEST1234.png')
