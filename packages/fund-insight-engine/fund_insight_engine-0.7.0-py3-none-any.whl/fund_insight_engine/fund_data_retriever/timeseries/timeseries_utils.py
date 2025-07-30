from fund_insight_engine.mongodb_retriever.menu8186_retriever.menu8186_utils import (
    fetch_data_menu8186_by_fund, 
    get_df_menu8186_by_fund
)
from .timeseries_consts import COLUMNS_FOR_TIMESERIES, KEYS_FOR_TIMESERIES

def set_index_of_timeseries(df):
    df = df.set_index('일자').rename_axis('date')
    return df

def get_df_timeseries_by_fund(fund_code, start_date=None, end_date=None, keys_to_project=KEYS_FOR_TIMESERIES):
    df = get_df_menu8186_by_fund(fund_code=fund_code, start_date=start_date, end_date=end_date, keys_to_project=keys_to_project)
    df = (
        df
        .copy()
        .pipe(set_index_of_timeseries)
    )
    return df


def slice_timeseries(df, start_date=None, end_date=None):
    if start_date is None and end_date is None:
        return df
    if start_date is None:
        return df[:end_date]
    if end_date is None:
        return df[start_date:]
    return df[start_date:end_date]

def get_raw_timeseries(fund_code, start_date=None, end_date=None):
    df = get_df_menu8186_by_fund(fund_code=fund_code, start_date=start_date, end_date=end_date)
    return df

def project_timeseries(df, columns=COLUMNS_FOR_TIMESERIES):
    return df[columns]