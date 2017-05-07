#!/usr/bin/python
import datetime
import logging, time


def check_dates(start_date, end_date):
    accepted_formats = ["%Y-%m-%d", "%Y-%m-%dT%H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%fZ" ]

    for f in accepted_formats:
        try: start = datetime.datetime.strptime( start_date, f )
        except ValueError: start = -1

        if start != -1: break

    for f in accepted_formats:
        try: end = datetime.datetime.strptime( end_date, f )
        except ValueError: end = -1

        if end != -1: break

    e = ''
    if start == -1: e = 'start_date: '+start_date
    if end == -1: e = 'end_date: '+end_date
    if start == -1 and end == -1: e = 'start_date and end_time'
    if e != '':
        raise ValueError('bad format in '+e+''
                        '\n accepted formats:\n' +
                        '  '.join(accepted_formats))

    if start > end: return (end, start)
    return (start,end)


def check_true_false(string):
    if string.lower() == 'true':
        return True
    if string.lower() == 'false':
        return False

    raise ValueError('bad format for true/false parameter: '+string)
    return None

logger1 = logging.getLogger('measure_time')
def measure_time(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        logger1.info( "function(%s): %2.2fs" % (method.__name__, te-ts) )
        return result

    return timed

@measure_time
def time_tester():
    for a in range(1,200):
        pow(2,a)


if __name__ == '__main__':
    print ("check_dates")
    print (check_dates("2017-04-21T06:38:19.861Z", "2017-04-03"))
    time_tester()
