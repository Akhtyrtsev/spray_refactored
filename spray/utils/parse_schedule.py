import datetime

HOURS = ['00:00 AM', '00:30 AM', '01:00 AM', '01:30 AM', '02:00 AM', '02:30 AM', '03:00 AM', '03:30 AM', '04:00 AM',
         '04:30 AM', '05:00 AM', '05:30 AM', '06:00 AM', '06:30 AM', '07:00 AM', '07:30 AM', '08:00 AM', '08:30 AM',
         '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '01:00 PM',
         '01:30 PM', '02:00 PM', '02:30 PM', '03:00 PM', '03:30 PM', '04:00 PM', '04:30 PM', '05:00 PM', '05:30 PM',
         '06:00 PM', '06:30 PM', '07:00 PM', '07:30 PM', '08:00 PM', '08:30 PM', '09:00 PM', '09:30 PM', '10:00 PM',
         '10:30 PM', '11:00 PM', '11:30 PM'
         ]


def sort_time(times):
    first_part = sorted(list(filter(lambda x: 'AM' in x, times)))
    second_part = sorted(list(filter(lambda x: 'PM' in x, times)))
    try:
        second_part.pop(second_part.index('12:30 PM'))
        second_part.insert(0, '12:30 PM')
    except Exception:
        pass
    try:
        second_part.pop(second_part.index('12:00 PM'))
        second_part.insert(0, '12:00 PM')
    except Exception:
        pass

    return first_part + second_part


def format_time(date):
    if date.time() < datetime.time(hour=12, minute=0, second=0):
        result = date.strftime('%H:%M AM')
    elif date.time() >= datetime.time(hour=13, minute=0, second=0):
        date = date - datetime.timedelta(hours=12)
        result = date.strftime('%H:%M PM')
    else:
        result = date.strftime('%H:%M PM')
    return result


def get_time_range(time, date=None):
    try:
        time = time['data']
        result = []
        for item in time:
            try:
                start = item['start']
                if start == '12:00 AM':
                    start = '00:00 AM'
                if date:
                    start = format_time(date)
                to = item['to']
                if to == '12:00 AM':
                    to = '00:00 AM'
                if start == to and start:
                    result = HOURS
                    continue
                start_index = HOURS.index(start)
                if date:
                    start_index -= 1
                    if start_index < 0:
                        start_index = 0
                if to == '00:00 AM':
                    result += HOURS[start_index:]
                else:
                    result += HOURS[start_index: HOURS.index(to)]
            except Exception:
                pass
        return result
    except Exception:
        return []
