'''
Module containing functions to ompute various metrics quantifying the
evolution of the queues.
'''

import pandas as pd


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
