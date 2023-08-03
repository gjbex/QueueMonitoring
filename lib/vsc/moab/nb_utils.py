from datetime import datetime, timedelta

def preprocess_active(df):
    rename = {
        'duration': 'remaining',
        'datetime': 'start_time',
        'derived': 'walltime_limit',
    }
    return df.rename(rename, axis='columns')

def preprocess_eligible(df):
    rename = {
        'duration': 'walltime_limit',
        'datetime': 'queue_time',
        'derived': 'time_in_queue',
    }
    return df.rename(rename, axis='columns')

def extract_category(df, category):
    new_df = df.query(f"category == '{category}'")
    if category == 'ActiveJob':
        new_df = preprocess_active(new_df)
    elif category in ['EligibleJob', 'BlockedJob']:
        new_df = preprocess_eligible(new_df)
    return new_df
