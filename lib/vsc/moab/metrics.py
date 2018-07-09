'''
Module containing functions to ompute various metrics quantifying the
evolution of the queues.
'''

import pandas as pd
from lib.vsc.moab.nb_utils import extract_category


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


def showq_started_vs_finished(directory, pattern):
    '''
    Compute a time series for the number of jobs starts, versus the
    number that ends during an epoch`.
      directory: Path to the directory containing the showq data files
      pattern: file name pattern for the showq data files
      returns pandas data frame representing a time series of the number
        of jobs in particular states
    '''
    file_names = list(directory.glob(pattern))
    prev_df = pd.read_csv(file_names.pop(0))
    prev_running_df = extract_category(prev_df, 'AcitveJob')
    prev_idle_df = extract_category(prev_df, 'EligibleJob')
    prev_blocked_df = extract_category(prev_df, 'BlockedJob')
    index = list()
    data = {
        'started': list(),
        'finished': list(),
    }
    for file_name in directory.glob(pattern):
        curr_df = pd.read_csv(file_name)
        index.append(get_time_stamp(curr_df))
        curr_running_df = extract_category(curr_df, 'ActiveJob')
        started_df = started_jobs(curr_running=curr_running_df,
                                  prev_idle=prev_idle_df,
                                  prev_blocked=prev_blocked_df)
        finished_df = finished_jobs(prev_running=prev_running_df,
                                    curr=curr_df)
        data['started'].append(len(started_df))
        data['finished'].append(-len(finished_df))
        prev_df = curr_df
        prev_running_df = curr_running_df
        prev_idle_df = extract_category(prev_df, 'EligibleJob')
        prev_blocked_df = extract_category(prev_df, 'BlockedJob')
    diff_df = pd.DataFrame(data, index=index)
    diff_df.sort_index(inplace=True)
    return diff_df


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


def finished_jobs(prev_running, curr):
    '''
    Compute the jobs that were running in the previous epoch, and
    that are no longer in the queue system.
      prev_running: pandas data frame containing the jobs that were
        active in the previous epoch
      curr: pandas data frame containing all jobs currently in the queues
      returns data frame representing the jobs that ended since the
        previous epoch
    '''
    return new_jobs(prev_running, curr)


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
