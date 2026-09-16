from datetime import datetime
from io import StringIO

import pandas as pd


class Loader:
    """Loads an UVV CSV file
    TODO: add Name of the spectrometer and file type
    """

    def __init__(self, filename, metadata=None, wl=420):
        self.filename = filename
        self.wl = wl
        # with open (self.filename, 'rb') as f:
        #     self._file = f

        self._metadata = metadata

    @property
    def _file(self):
        with open(self.filename, "rb") as f:
            return f

    @property
    def file(self):
        r"""
        A file like object of the loaded CSV.

        EXAMPLES::
            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = CSVloader(file)
            >>> type(csv.file)
            <class '_io.StringIO'>

        """
        return StringIO(self.file)

    @property
    def lines(self):
        """List of lines of the original CSV."""
        with open(self.filename, "rb") as f:
            return f.readlines()

    @property
    def df_original(self):
        return pd.read_csv(self.filename)

    @property
    def columns(self):
        return self.df_original.columns

    @property
    def metadata_index(self):
        return self.df_original[
            self.df_original[self.columns[0]] == self.columns[0]
        ].index.values.tolist()[0]

    @property
    def device_csv_metadata(self):
        """
        TODO. remove '\r\n'
        """
        metadata = []
        for i in range(self.metadata_index + 3, self.metadata_index + 32):
            # the end range should be determined automatically,
            # just in case that the software decides
            # to change the number of metadata lines
            metadata.append(self.lines[i].decode("utf-8"))

        return metadata

    @property
    def df_truncated(self):
        """Truncated df, where the last empty column
        and the metadata at the tail is removed.
        """
        # remove last empty column
        df_truncated_ = self.df_original[: self.metadata_index]
        # remove second line
        return df_truncated_.drop(columns=self.columns[-1])

    @property
    def df(self):
        df_ = self.df_truncated.drop([0]).reset_index(drop=True)
        df_.columns = ["lambda", "abs"]
        # Since in the original df strings were mixed with numbers
        # we have to set the data type of the df manually.
        return df_.astype("float")

    @property
    def get_measurement_time(self):
        # TODO: extract time with regex
        date_string = self.device_csv_metadata[1][17:-2]
        date_format = "%m/%d/%Y %I:%M:%S %p"
        return datetime.strptime(date_string, date_format)

    @property
    def date(self):
        return self.get_measurement_time.date().isoformat()

    @property
    def time(self):
        return self.get_measurement_time.time().isoformat().replace(":", "")

    @property
    def metadata(self):
        meta = {
            "device measurement metadata": self.device_csv_metadata,
            # 'filename': self.filename,
            "date": self.date,
            "time": self.time,
           # "absorbance 420": self.get_absorbance,
        }

        return meta

    @property
    def csv_name(self):
        return f"{self.date}_{self.time}_spotX.csv"
