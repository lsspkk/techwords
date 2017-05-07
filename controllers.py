#!/usr/bin/python
import json, operator
from datetime import datetime, timedelta
from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import sessionmaker

from models import TechWord, Day, Advertisement, Match
import models

def get_techwords():
    s = models.Session()
    words = s.query(TechWord).all()
    s.commit()
    return words

def get_techword(word):
    s = models.Session()
    word = s.query(TechWord).filter_by(word=word).all()
    s.commit()
    return word

def get_advertisement(id):
    s = models.Session()
    ad = s.query(Advertisement).filter(Advertisement.id==id).all()
    s.commit()
    return ad

def get_advertisements(start='',end=''):
    s = models.Session()
    if start == '' or end == '':
        ads = s.query(Advertisement).all()
        s.commit()
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
    s.commit()
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
    s.commit()

    return counts


def _format(date):
    return "%4d-%2d-%2d" % (date.year, date.month, date.day)

def get_techword_counts(start=datetime(2017,1,1), end=datetime.now()):
    # search full days including the end day
    start = start.replace(hour=1,minute=0)
    end = end.replace(hour=0,minute=0)
    end = end + timedelta(days=1)
    day = start

    s = models.Session()
    words = s.query(TechWord)
    counts = {}
    while day <= end:
        toDate = day + timedelta(days=1)
        counts[day.strftime('%Y-%m-%d')] = []
        for tw in words:
            d = s.query(Match).filter(Match.date >= day,
                                      Match.date < toDate,
                                      Match.techword_id == tw.id).all()
            if len(d) > 0:
                counts[day.strftime('%Y-%m-%d')].append({ 'word': tw.word, 'count': d[0].count })
        day = day + timedelta(days=1)
    s.commit()

    return counts



if __name__ == '__main__':
    print ('get_counts')
    print (json.dumps(get_total_counts(datetime(2017,4,2)),indent=4,sort_keys=True))

    print ('get_techword_counts')
    print (json.dumps(get_techword_counts(datetime(2017,4,19),datetime(2017,4,19)),indent=4,sort_keys=True))
