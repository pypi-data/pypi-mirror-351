import pandas as pd
from .index_transformer import map_dates_str_to_datetimes, map_datetimes_to_dates_str, map_datetimes_to_unix_timestamps, map_dates_str_to_unix_timestamps, map_unix_timestamps_to_datetimes
from .index_validator import is_valid_dataframe, is_datetime_index, is_string_index, is_unix_timestamp_index, validate_index_type

def transform_to_timeseries_with_str(timeseries):
    is_valid_dataframe(timeseries)
    df = timeseries.copy()
    
    if is_datetime_index(df.index):
        df.index = map_datetimes_to_dates_str(df.index)
    elif is_unix_timestamp_index(df.index):
        df.index = map_datetimes_to_dates_str(map_unix_timestamps_to_datetimes(df.index))
    elif not is_string_index(df.index):
        validate_index_type(df.index)
    
    return df

def transform_to_timeseries_with_datetime(timeseries):
    is_valid_dataframe(timeseries)
    df = timeseries.copy()
    
    if is_datetime_index(df.index):
        return df
    elif is_string_index(df.index):
        try:
            df.index = map_dates_str_to_datetimes(df.index)
        except Exception as e:
            raise ValueError(f"Failed to convert string index to datetime: {str(e)}")
    elif is_unix_timestamp_index(df.index):
        try:
            df.index = map_unix_timestamps_to_datetimes(df.index)
        except Exception as e:
            raise ValueError(f"Failed to convert unix timestamp to datetime: {str(e)}")
    else:
        validate_index_type(df.index)
    
    return df

def transform_to_timeseries_with_unix_time(timeseries):
    is_valid_dataframe(timeseries)
    df = timeseries.copy()
    
    if is_datetime_index(df.index):
        df.index = map_datetimes_to_unix_timestamps(df.index)
    elif is_string_index(df.index):
        try:
            df.index = map_dates_str_to_unix_timestamps(df.index)
        except Exception as e:
            raise ValueError(f"Failed to convert string index to unix time: {str(e)}")
    elif not is_unix_timestamp_index(df.index):
        validate_index_type(df.index)
    
    return df


def transform_timeseries(timeseries, option_type):
    if not isinstance(timeseries, pd.DataFrame):
         raise TypeError("Input must be a pandas DataFrame")
         
    mapping_transformer = {
         'str': transform_to_timeseries_with_str,
         'datetime': transform_to_timeseries_with_datetime,
         'unix_time': transform_to_timeseries_with_unix_time
    }
    
    if option_type not in mapping_transformer:
         raise ValueError("option_type must be either 'str' or 'datetime'", "'unix_time'")
         
    transformer = mapping_transformer[option_type]
    timeseries = transformer(timeseries)
    print(f"Transformed timeseries to {type(timeseries.index[0])} index")
    return timeseries

