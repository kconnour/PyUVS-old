from pyuvs.l1b.data_contents import L1bDataContents
from pyuvs.files import DataFilename


class DataClassifier:
    """Create an object that can classify L1b data.

    DataClassifier can classify a single data file.

    """
    def __init__(self, data: DataFilename):
        """
        Parameters
        ----------
        data
            The data file to classify.

        """
        self.contents = L1bDataContents(data)

    def single_integration(self) -> bool:
        """Determine if the data file is a single integration.

        """
        return self.contents.n_integrations == 1

    def dayside(self) -> bool:
        """Determine if the data file was taken with dayside voltage settings.

        """
        return self.contents.mcp_volt < 790
