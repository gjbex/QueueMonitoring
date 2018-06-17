from datetime import datetime, timedelta

def preprocess_active(df):
    rename = {
        'duration': 'remaining',
        'datetime': 'start_time',
        'derived': 'walltime_limit',
    }
    new_df = df.rename(rename, axis='columns')
    return new_df

def preprocess_eligible(df):
    rename = {
        'duration': 'walltime_limit',
        'datetime': 'queue_time',
        'derived': 'time_in_queue',
    }
    new_df = df.rename(rename, axis='columns')
    return new_df

def extract_category(df, category):
    new_df = df.query(f"category == '{category}'")
    if category == 'ActiveJob':
        new_df = preprocess_active(new_df)
    elif category == 'EligibleJob' or category == 'BlockedJob':
        new_df = preprocess_eligible(new_df)
    return new_df
