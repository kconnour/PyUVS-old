class DataProperties:
    def __init__(self, filenames):
        self.filenames = filenames

    @property
    def n_files(self):
        return len(self.filenames)
