#!/usr/bin/env python

import re
import sys

from vsc.moab.jobs import ActiveJob, EligibleJob, BlockedJob


def fix_time(line, time_stamp):
    return f'{line} {time_stamp.year}'

def parse_jobs(in_file, time_stamp, cls, end_re, last_line_handler=None):
    jobs = []
    _ = in_file.readline().rstrip().split()    # read headers
    for line in in_file:
        line = line.strip()
        if not line:
            continue
        if re.match(end_re, line):
            if last_line_handler:
                last_line_handler(in_file)
            break
        line = fix_time(line, time_stamp)
        jobs.append(cls.parse(line, time_stamp))
    return jobs


def active_job_last_line_handler(in_file):
    _ = in_file.readline()

def parse_showq_output(in_file, time_stamp):
    for line in in_file:
        line = line.strip()
        if not line:
            continue
        if line.startswith('active jobs'):
            active_jobs = parse_jobs(in_file, time_stamp, ActiveJob,
                                     r'^\s*\d+\s+active jobs',
                                     active_job_last_line_handler)
            continue
        if line.startswith('eligible jobs'):
            eligible_jobs = parse_jobs(in_file, time_stamp, EligibleJob,
                                       r'^\s*\d+\s+eligible jobs')
            continue
        if line.startswith('blocked jobs'):
            blocked_jobs = parse_jobs(in_file, time_stamp, BlockedJob,
                                      r'^\s*\d+\s+blocked jobs')
            continue
        if re.match(r'^Total jobs:\s*\d+$', line):
            break
    return active_jobs, eligible_jobs, blocked_jobs

def format_job(job, time_stamp, sep=','):
    str_list = [
        f'{type(job).__name__}',
        f'{time_stamp}',
        f'{job.jobid}',
        f'{job.username}',
        f'{job.state}',
        f'{job.procs}',
    ]
    if isinstance(job, ActiveJob):
        str_list.append(f'{int(job.remaining.total_seconds())}')
        str_list.append(f'{job.starttime}')
        str_list.append(f'{job.wclimit.total_seconds()}')
    elif isinstance(job, EligibleJob):
        str_list.append(f'{int(job.wclimit.total_seconds())}')
        str_list.append(f'{job.queuetime}')
        str_list.append(f'{job.time_in_queue.total_seconds()}')
    return sep.join(str_list)
        
def write_header(out_file, sep=','):
    columns = [
        'category', 'time_stamp', 'job_id', 'user_id', 'state', 'procs',
        'duration', 'datetime', 'derived',
    ]
    print(sep.join(columns), file=out_file)

def write_jobs(out_file, job_list, time_stamp, sep=','):
    for job in job_list:
        print(format_job(job, time_stamp, sep), file=out_file)


if __name__ == '__main__':
    from argparse import ArgumentParser
    from datetime import datetime

    arg_parser = ArgumentParser(description='Convert showq output to '
                                            'CSV format')
    arg_parser.add_argument('--input', help='file containing showq output')
    arg_parser.add_argument('--output', help='file to write CSV to')
    arg_parser.add_argument('--time',
                            help='time showq was executed, format, e.g., '
                                 ' Wed Jun  6 08:53:16 CEST 2018; if not '
                                 'given, now is assumed')
    arg_parser.add_argument('--sep', default=',', help='output seprator')
    options = arg_parser.parse_args()
    if options.time:
        time_stamp = datetime.strptime(options.time, '%a %b %d %H:%M:%S %Z %Y')
    else:
        time_stamp = datetime.now()
    if options.input:
        in_file = open(options.input, 'r')
    else:
        in_file = sys.stdin
    if options.output:
        out_file = open(options.output, 'w')
    else:
        out_file = sys.stdout
    write_header(out_file, options.sep)
    for job_list in parse_showq_output(in_file, time_stamp):
        write_jobs(out_file, job_list, time_stamp, options.sep)
    if options.input:
        in_file.close()
    if options.output:
        out_file.close()
