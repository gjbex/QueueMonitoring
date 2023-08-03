#!/usr/bin/env python

from datetime import datetime
import re
import sys
from typing import Optional

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
        str_list.extend((f'{int(job.remaining.total_seconds())}', f'{job.starttime}'))
        str_list.append(f'{job.wclimit.total_seconds()}')
    elif isinstance(job, EligibleJob):
        str_list.extend((f'{int(job.wclimit.total_seconds())}', f'{job.queuetime}'))
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


def time_from_filename(filename: str) -> Optional[datetime]:
    if match := re.search(r'_(\d+)\.', filename):
        unix_time = int(match[1])
        return datetime.fromtimestamp(unix_time)
    else:
        return None


if __name__ == '__main__':
    from argparse import ArgumentParser

    arg_parser = ArgumentParser(description='Convert showq output to '
                                            'CSV format')
    arg_parser.add_argument('--input', help='file containing showq output')
    arg_parser.add_argument('--output', help='file to write CSV to')
    arg_parser.add_argument('--time',
                            help='time showq was executed, format, e.g., '
                                 ' Wed Jun  6 08:53:16 CEST 2018; if not '
                                 'given, now is assumed')
    arg_parser.add_argument('--sep', default=',', help='output seprator')
    arg_parser.add_argument('--quiet', action='store_true',
                            help='do not print info')
    options = arg_parser.parse_args()
    if options.time:
        time_stamp = datetime.strptime(options.time,
                                       '%a %b %d %H:%M:%S %Z %Y')
    elif options.input:
        time_stamp = time_from_filename(options.input)
    if not time_stamp:
        time_stamp = datetime.now()
        if not options.quiet:
            print('### warning: no timestamp found, using now',
                  file=sys.stderr)
    in_file = open(options.input, 'r') if options.input else sys.stdin
    out_file = open(options.output, 'w') if options.output else sys.stdout
    write_header(out_file, options.sep)
    for job_list in parse_showq_output(in_file, time_stamp):
        write_jobs(out_file, job_list, time_stamp, options.sep)
    if options.input:
        in_file.close()
    if options.output:
        out_file.close()
