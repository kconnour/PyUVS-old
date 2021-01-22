import os


def get_project_path() -> str:
    """ Get the absolute path of the project.

    Returns
    -------
    path: str
        Absolute path of the project.
    """
    return os.path.abspath(os.path.join(os.path.dirname(
        os.path.realpath(__file__)), '../..'))
