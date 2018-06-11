from datetime import datetime, timedelta

def preprocss_running(df):
    rename = {
        'duration': 'remaining',
        'datetime': 'start_time',
        'derived': 'walltime_limit',
    }
    new_df = df.rename(rename, axis='columns')
    return new_df

def preprocss_idle(df):
    rename = {
        'duration': 'walltime_limit',
        'datetime': 'queue_time',
        'derived': 'time_in_queue',
    }
    new_df = df.rename(rename, axis='columns')
    return new_df

def extract_state(df, state):
    new_df = df.query(f"state == '{state}'")
    if state == 'Running':
        new_df = preprocss_running(new_df)
    elif state == 'Idle' or state == 'Blocked':
        new_df = new_df = preprocss_idle(new_df)
    return new_df
