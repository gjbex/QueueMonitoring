'''
module that defines classes to represent jobs as defined by Moab's
showq output.
'''

from datetime import datetime, timedelta
from typing import List, Optional, Union


def duration2seconds(duration: str) -> int:
    periods = duration.split(':')
    factors: List[int] = [1, 60, 60*60, 24*60*60]
    return sum(map(lambda x: x[0]*x[1],
                   zip(factors, map(int, periods[::-1]))))

class Job:

    def __init__(self, jobid: str, username: str, state: str,
                 procs: Union[str, int]) -> None:
        self._jobid = jobid
        self._username = username
        self._state = state
        self._procs = int(procs)

    @property
    def jobid(self) -> str:
        return self._jobid

    @property
    def username(self) -> str:
        return self._username

    @property
    def state(self) -> str:
        return self._state

    @property
    def procs(self) -> int:
        return self._procs

    @staticmethod
    def _parse_time_str(time_str: str) -> datetime:
        return datetime.strptime(time_str, '%c')

    @classmethod
    def parse(cls, job_str, time_stamp):
        data = job_str.strip().split(maxsplit=5)
        return cls(*data, time_stamp)
                

class ActiveJob(Job):

    def __init__(self, jobid: str, username: str, state: str,
                 procs: Union[str, int], remaining: str, starttime: str,
                 time_stamp=Optional[datetime]) -> None:
        super().__init__(jobid, username, state, procs)
        self._remaining = timedelta(seconds=duration2seconds(remaining))
        self._starttime = Job._parse_time_str(starttime)
        self._wctime: Optional[timedelta] = None
        if time_stamp is not None:
            self.set_wctime(time_stamp)

    @property
    def remaining(self) -> timedelta:
        return self._remaining

    @property
    def starttime(self) -> datetime:
        return self._starttime

    def set_wctime(self, time_stamp: datetime):
        self._wctime = time_stamp - self.starttime
        
    @property
    def wctime(self):
        return self._wctime

    @property
    def wclimit(self):
        if self.wctime is not None:
            return self.wctime + self.remaining
        else:
            return None


class EligibleJob(Job):

    def __init__(self, jobid, username, state, procs,
                 wclimit, queuetime, time_stamp=None):
        super().__init__(jobid, username, state, procs)
        self._wclimit = timedelta(seconds=duration2seconds(wclimit))
        self._queuetime = Job._parse_time_str(queuetime)
        self._time_in_queue = None
        if time_stamp:
            self.set_time_in_queue(time_stamp)

    @property
    def wclimit(self):
        return self._wclimit

    @property
    def queuetime(self):
        return self._queuetime

    def set_time_in_queue(self, time_stamp):
        self._time_in_queue = time_stamp - self.queuetime

    @property
    def time_in_queue(self):
        return self._time_in_queue


class BlockedJob(EligibleJob):
    pass
