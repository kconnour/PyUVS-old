from pyuvs.l1b.data_contents import L1bDataContents


class DataClassifier:
    def __init__(self, fname: str):
        self.contents = L1bDataContents(fname)

    def single_integration(self) -> bool:
        return self.contents.primary.ndim == 2

    def dayside(self) -> bool:
        return self.contents.voltage < 790
