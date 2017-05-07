#!/usr/bin/python
import json, operator
from datetime import datetime, timedelta
from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import sessionmaker

# http://docs.sqlalchemy.org/en/latest/faq/performance.html
import cProfile
from io import StringIO
import pstats
import contextlib
import logging


@contextlib.contextmanager
def profiled():
    pr = cProfile.Profile()
    pr.enable()
    yield
    pr.disable()
    s = StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    # uncomment this to see who's calling what
    # ps.print_callers()
    logging.info(s.getvalue())


from models import TechWord, Day, Advertisement, Match
import models

def get_techwords():
    s = models.Session()
    words = s.query(TechWord).all()
    s.expunge_all(); s.close()
    return words

def get_techword(word):
    s = models.Session()
    word = s.query(TechWord).filter_by(word=word).all()
    s.expunge_all(); s.close()
    return word

def get_advertisement(id):
    s = models.Session()
    ad = s.query(Advertisement).filter(Advertisement.id==id).all()
    s.expunge_all(); s.close()
    return ad

def get_advertisements(start='',end=''):
    s = models.Session()
    if start == '' or end == '':
        ads = s.query(Advertisement).all()
        s.expunge_all(); s.close()
        return ads


    # search full days including the end day
    start = start.replace(hour=0,minute=0,second=0)
    end = end.replace(hour=0,minute=0)
    end = end + timedelta(days=1)

    # ad is in the range in all these cases
    # - start_date is in range
    # - end_date is in range
    # - range is between start_date and end_date

    ads = s.query(Advertisement).filter(
        or_(
            and_(Advertisement.start_date <= start, models.Advertisement.end_date >= start),
            and_(Advertisement.start_date <= end, models.Advertisement.end_date >= end),
            and_(Advertisement.start_date >= start, models.Advertisement.end_date <= end)
            )).all()
    s.expunge_all(); s.close()
    return ads


# return indexes, where match was found
def match_result(ad, words):
    matches = []
    tl = ad.text.lower()
    for tw in words:
        ss = json.loads(tw.search_strings)
        for search_string in ss:
            i = tl.find(search_string)
            if i >= 0:
                matches.append({'word':tw.word,
                                'search_string':search_string,
                                'index':i})
                break
    sorted_matches = sorted(matches,key=operator.itemgetter('index'))
    return sorted_matches


def get_total_counts(start=datetime(2017,1,1), end=datetime.now()):
    # search full days including the end day
    start = start.replace(hour=1,minute=0)
    end = end.replace(hour=0,minute=0)
    end = end + timedelta(days=1)
    day = start

    s = models.Session()
    counts = {}
    while day <= end:
        toDate = day + timedelta(days=1)
        d = s.query(Day).filter(Day.date >= day, models.Day.date <= toDate).all()
        if len(d) > 0:
            counts[day.strftime('%Y-%m-%d')] = d[0].count;
        day = day + timedelta(days=1)
    s.expunge_all(); s.close()

    return counts


def _format(date):
    return "%4d-%2d-%2d" % (date.year, date.month, date.day)

def get_techword_counts(start=datetime(2017,1,1), end=datetime.now()):
    # search full days including the end day
    start = start.replace(hour=1,minute=0)
    end = end.replace(hour=0,minute=0)
    end = end + timedelta(days=1)

    s = models.Session()
    counts = {}
    # uncomment this to see db query timing results
    # with profiled():
    #    matches = s.query(Match).filter(Match.date >= start, Match.date < end).all()

    matches = s.query(Match).filter(Match.date >= start, Match.date < end).all()
    for m in matches:
        if m.date.strftime('%Y-%m-%d') not in counts:
            counts[m.date.strftime('%Y-%m-%d')] = []
        counts[m.date.strftime('%Y-%m-%d')].append({ 'word': m.techword, 'count': m.count })
    s.expunge_all(); s.close()

    return counts



if __name__ == '__main__':
    print ('get_counts')
    print (json.dumps(get_total_counts(datetime(2017,4,2)),indent=4,sort_keys=True))

    print ('get_techword_counts')
    print (json.dumps(get_techword_counts(datetime(2017,4,19),datetime(2017,4,19)),indent=4,sort_keys=True))
