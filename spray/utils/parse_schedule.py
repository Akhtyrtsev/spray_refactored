import datetime

import moment

HOURS = ['00:00 AM', '00:30 AM', '01:00 AM', '01:30 AM', '02:00 AM', '02:30 AM', '03:00 AM', '03:30 AM', '04:00 AM',
         '04:30 AM', '05:00 AM', '05:30 AM', '06:00 AM', '06:30 AM', '07:00 AM', '07:30 AM', '08:00 AM', '08:30 AM',
         '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '01:00 PM',
         '01:30 PM', '02:00 PM', '02:30 PM', '03:00 PM', '03:30 PM', '04:00 PM', '04:30 PM', '05:00 PM', '05:30 PM',
         '06:00 PM', '06:30 PM', '07:00 PM', '07:30 PM', '08:00 PM', '08:30 PM', '09:00 PM', '09:30 PM', '10:00 PM',
         '10:30 PM', '11:00 PM', '11:30 PM'
         ]


def parse_schedule(time):
    try:
        time = dict(time)['data']
        result = []
        for item in time:
            if item['start'] and item['to']:
                # format to 24h
                start = moment.date(item['start']).format('HH:mm')
                if start == '00:03':
                    start = '00:30'
                to = moment.date(item['to']).format('HH:mm')
                # if working full day
                if start == to:
                    if start == '00:00':
                        result.append((
                            datetime.datetime.strptime('00:00', '%H:%M').time(),
                            datetime.datetime.strptime('23:59', '%H:%M').time()
                        ))
                    continue

                start = datetime.datetime.strptime(start, '%H:%M').time()

                # case when working till the end of the day
                if to == "00:00":
                    to = datetime.datetime.strptime("23:59", '%H:%M').time()
                else:
                    # normal case
                    to = datetime.datetime.strptime(to, '%H:%M').time()
                # normal case
                if start < to:
                    result.append((start, to))
                # case when start 4pm, end 2pm, working hours = 22h total
                # else:
                #     result.append(
                #         (datetime.datetime.strptime('00:00', '%H:%M').time(), to))
                #     result.append(
                #         (start, datetime.datetime.strptime('23:59', '%H:%M').time()))
        return result
    except Exception:
        return []


def format_time(date):
    if date.time() < datetime.time(hour=12, minute=0, second=0):
        result = date.strftime('%H:%M AM')
    elif date.time() >= datetime.time(hour=13, minute=0, second=0):
        date = date - datetime.timedelta(hours=12)
        result = date.strftime('%H:%M PM')
    else:
        result = date.strftime('%H:%M PM')
    return result


def closest_to_now(time):
    original_time = time
    time = format_time(time)
    letters = time[-2:]
    check_in = list(filter(lambda x: letters in x, HOURS))
    check_in.append(time)
    check_in.sort()
    if letters == 'AM':
        check_in.append('12:00 PM')
    else:
        if original_time.hour == 12:
            last = check_in[-3:]
            check_in.pop(-1)
            check_in.pop(-1)
            check_in.pop(-1)
            check_in = last + check_in
        else:
            last = check_in[-2:]
            check_in.pop(-1)
            check_in.pop(-1)
            check_in = last + check_in
        check_in.append('00:00 AM')
    return check_in[check_in.index(time) + 1]


def parse_schedule_range(time):
    parsed_time = parse_schedule(time)
    result = set()
    for couple in parsed_time:
        start, to = couple
        for val in range(start.hour, to.hour):
            result.add(val)
        if to.minute >= 30:
            result.add(to.hour)
    return list(result)


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

