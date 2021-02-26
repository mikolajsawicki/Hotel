from datetime import datetime

class DateRangeException(Exception):
    pass

class Period:
    def __init__(self, start, end):
        if start >= end:
            raise DateRangeException('Start  date has to be earlier than end date.')
        self.start = start
        self.end = end

    def overlaps(self, period):
        return self.start <= period.end and self.end >= period.start

    def length(self):
        return self.end - self.start