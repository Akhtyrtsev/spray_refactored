import datetime
from datetimerange import DateTimeRange


def get_time_range(start, end):
    result = []
    end = datetime.datetime.combine(datetime.date.today(), end)
    end -= datetime.timedelta(minutes=30)
    end = end.time()
    time_range = DateTimeRange(str(start), str(end))
    for value in time_range.range(datetime.timedelta(minutes=30)):
        result.append(value.strftime('%H:%M'))
    return result
