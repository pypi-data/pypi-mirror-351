from string_date_controller import get_all_dates_between_dates
from logging import getLogger
logger = getLogger(__name__)

def slice_timeseries_by_dates(timeseries, start_date, end_date):
    df = timeseries.copy()
    if start_date:
        existing_start_date = df.loc[:start_date].index[-1]
        if end_date:
            df = df.loc[existing_start_date:end_date]
        else:
            df = df.loc[start_date:]
    elif end_date:
        df = df.loc[:end_date]
    return df

def get_dates_pair_of_timeseries(timeseries, start_date=None, end_date=None):
    initial_date, final_date = timeseries.index[0], timeseries.index[-1] 
    if start_date:
        initial_date = start_date if initial_date < start_date else initial_date
    if end_date:
        final_date = end_date if final_date > end_date else final_date
    return initial_date, final_date

def get_all_dates_for_timeseries(timeseries, start_date=None, end_date=None):
    initial_date, final_date = get_dates_pair_of_timeseries(timeseries, start_date, end_date)
    all_dates = get_all_dates_between_dates(initial_date, final_date)
    return all_dates

def extend_timeseries_by_all_dates(timeseries, start_date=None, end_date=None, option_verbose=False):
    df = timeseries.copy()
    if option_verbose:
        logger.info(f'(original) {df.index[0]} ~ {df.index[-1]}, {len(df)} days')
    all_dates = get_all_dates_for_timeseries(df, start_date, end_date)
    df_extended = df.reindex(all_dates).ffill()
    if option_verbose:
        logger.info(f'(extended) {df_extended.index[0]} ~ {df_extended.index[-1]}, {len(df_extended)} days')
    return df_extended
