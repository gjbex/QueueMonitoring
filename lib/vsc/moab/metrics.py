'''
Module containing functions to ompute various metrics quantifying the
evolution of the queues.
'''

import pandas as pd

def get_time_stamp(df):
    '''
    Return the time stemp of a showq data frame.
      df: pandas data frame representing showq output
      returns a pandas Datetime object
    '''
    return df.time_stamp.drop_duplicates()[0]

def showq_timeframe(showq_df):
    '''
    Compute a one-row data frame representing the number of jobs that
    are in a particular state.
      showq_df: pandas data frame representing showq information
      returns a pandas one-row data frame
    '''
    time_stamp = get_time_stamp(showq_df)
    state_distr = state_distribution(showq_df).transpose()
    state_distr.rename(index={'nr_jobs': time_stamp}, inplace=True)
    state_distr.index = pd.to_datetime(state_distr.index)
    return state_distr

def showq_timeseries(directory, pattern='showq_*.csv'):
    '''
    Compute a time series for the number of jobs that are in a particular
    state.
      directory: Path to the directory containing the showq data files
      pattern: file name pattern for the showq data files
      returns pandas data frame representing a time series of the number
        of jobs in particular states
    '''
    showq_files = list(directory.glob(pattern))
    showq_df = pd.read_csv(showq_files.pop(0))
    queues_time_series = showq_timeframe(showq_df)
    for file_name in showq_files:
        showq_df = pd.read_csv(file_name)
        new_row = showq_timeframe(showq_df)
        queues_time_series = pd.concat([queues_time_series, new_row],
                                       sort=False)
    queues_time_series.sort_index(inplace=True)
    return queues_time_series

def moved_jobs(from_cat, to_cat):
    '''
    Compute the number of jobs that have moved from one category to
    another since the previous epoch.
      from_cat: DataFrame containing the jobs in the previous epoch
      to_cat: DataFrame containing the jobs in the current epoch
      returns DataFrame with new jobs in the category
    '''
    moved = to_cat.merge(from_cat, on='job_id', how='inner',
                         suffixes=['', '_from'])
    return moved[to_cat.columns]

def started_jobs(curr_running, prev_idle, prev_blocked):
    '''
    Compute the jobs that started since the previous epoch.
      curr_running: DataFrame containing the currently yrunning jobs
      prev_idle: DataFrame containing the jobs idle in the previous epoch
      prev_blocked: DataFrame containing the jobs blocked in the previous
                    epoch
      returns DataFrame with newly running jobs
    '''
    prev_inactive = pd.concat([prev_idle, prev_blocked],
                              ignore_index=True)
    return moved_jobs(from_cat=prev_inactive, to_cat=curr_running)

def new_jobs(curr, prev):
    '''
    Compute the number of jobs that are new in this category since the
    previous epoch.
      curr: DataFrame containing the jobs in the current epoch
      prev: DataFrame containing the jobs in the previous epoch
      returns DataFrame with new jobs in the category
    '''
    return curr[~curr.job_id.isin(prev.job_id)]

def state_distribution(jobs):
    return jobs[['job_id', 'state']].groupby('state').count() \
                                    .rename(columns={'job_id': 'nr_jobs'})
