import numpy as np
from universal_timeseries_transformer.timeseries_transformer import transform_timeseries

class TimeseriesMatrix:
    def __init__(self, df):
        self.df = df
        self.dates = list(df.index)
        self._basis = None
        self._datetime = None
        self._unixtime = None
        self._string = None
    
    @property
    def basis(self):
        if self._basis is None:
            self._basis = np.array(self.dates)
        return self._basis

    @property
    def date_i(self):
        return self.dates[0]
    
    @property
    def date_f(self):
        return self.dates[-1]

    def row(self, i):
        return self.df.iloc[[i], :]

    def column(self, j):
        return self.df.iloc[:, [j]]
        
    def row_by_name(self, name):
        return self.df.loc[[name], :]

    def column_by_name(self, name):
        return self.df.loc[:, [name]]

    def component(self, i, j):
        return self.df.iloc[i, j]

    def component_by_name(self, name_i, name_j):
        return self.df.loc[name_i, name_j]

    def rows(self, i_list):
        return self.df.iloc[i_list, :]
        
    def columns(self, j_list):
        return self.df.iloc[:, j_list]

    def rows_by_names(self, names):
        return self.df.loc[names, :]
        
    def columns_by_names(self, names):
        return self.df.loc[:, names]

    def datetime(self):
        if self._datetime is None:
            self._datetime = transform_timeseries(self.df, 'datetime')
        return self._datetime

    def unixtime(self):
        if self._unixtime is None:
            self._unixtime = transform_timeseries(self.df, 'unix_timestamp')
        return self._unixtime

    def string(self):
        if self._string is None:
            self._string = transform_timeseries(self.df, 'str')
        return self._string
