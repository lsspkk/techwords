#!/usr/bin/python
import json, datetime, sys
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Sequence, DateTime
from sqlalchemy.orm import sessionmaker


import manage_data


Base = declarative_base()


class TechWord(Base):
    __tablename__ = 'techword'
    id = Column(Integer, Sequence('tech_word_seq'),primary_key=True)
    word = Column(String(24))
    search_strings = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'tech_word' :  self.word,
            'search_strings' : json.loads(self.search_strings)
        }

    def __repr__(self):
       return "<TechWord(word='%s', search_strings='%s')>" % (
                            self.word, self.search_strings)


class Advertisement(Base):
    __tablename__ = 'advertisement'
    id = Column(Integer,primary_key=True)
    title = Column(String)
    job = Column(String)
    text = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    @property
    def serialize(self):
        return {
            'id' :  self.id,
            'title' :  self.title,
            'start_date' :  self.start_date,
            'end_date' :  self.end_date
        }

    @property
    def serialize_with_text(self):
        return {
            'id' :  self.id,
            'title' :  self.title,
            'start_date' :  self.start_date,
            'end_date' :  self.end_date,
            'text' : self.text
        }



class Day(Base):
    __tablename__ = 'day'
    id = Column(Integer, Sequence('day_id'),primary_key=True)
    date = Column(DateTime)
    count = Column(Integer)

class Match(Base):
    __tablename__ = 'match'
    id = Column(Integer, Sequence('match_seq'),primary_key=True)
    date = Column(DateTime)
    techword_id = Column(Integer)
    count = Column(Integer)




engine = create_engine(manage_data.database_file)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)




def init_techwords():
    s = Session()
    words = s.query(TechWord)
    for w in words: s.delete(w)

    words = manage_data.get_techwords()
    for w in words:
        tw = TechWord(word=w['word'], search_strings=json.dumps(w['search_strings']).lower())
        s.add(tw)
    s.commit()

def init_advertisements():
    s = Session()
    ads = s.query(Advertisement)
    for a in ads: s.delete(a)

    ads = manage_data.get_advertisements()
    for a in ads:
        start = datetime.strptime( a['start_date'], "%Y-%m-%dT%H:%M:%S")
        end = datetime.strptime( a['end_date'], "%Y-%m-%dT%H:%M:%S")

        ad = Advertisement(id=a['id'],
                           job=a['job'],
                           title=a['title'],
                           text=a['text'],
                           start_date=start,
                           end_date=end)
        s.add(ad)

    s.commit()






def search_techwords_from_ad(text, tech_words, results):
    tl = text.lower()
    for tw in tech_words:
        for search_string in tw['search_strings']:
            i = tl.find(search_string)
            if i >= 0:
                results[tw['id']] = results[tw['id']] + 1
                #print "loytyi", search_string
                break
#

# to Database
#   add Day -objects for each day of year when this ad is on
#        for each day, count the advertisements
#   add Match -objects for each day of year and every techword
#        for each match, update with the search results
#
def store_results_for_all_dates(ad, results, s):
    day = datetime(ad.start_date.year, ad.start_date.month, ad.start_date.day)
    while day <= ad.end_date:
        toDate = day + timedelta(days=1)
        d = s.query(Day).filter(Day.date >= day, Day.date < toDate).all()

        if len(d) == 0:
            new_d = Day(date=day,count=1)
            s.add(new_d)
        elif len(d) == 1:
            d[0].count = d[0].count + 1

        for key in results:
            m = s.query(Match).filter(Match.date >= day,
                                            Match.date < toDate,
                                            Match.techword_id == key).all()
            if len(m) == 0:
                new_m = Match(techword_id=key,count=results[key],date=day)
                s.add(new_m)
            elif len(m) == 1:
                m[0].count = m[0].count + results[key]
                #print day, '-', toDate, '-->', m[0].count

        day = day + timedelta(days=1)




def add_new_advertisements():
    s = Session()

    ads = manage_data.get_advertisements()
    for a in ads:
        old = s.query(Advertisement).filter(Advertisement.id == a['id']).all()
        if len(old) != 0:
            continue

        start = datetime.strptime( a['start_date'], "%Y-%m-%dT%H:%M:%S")
        end = datetime.strptime( a['end_date'], "%Y-%m-%dT%H:%M:%S")

        ad = Advertisement(id=a['id'],
                           job=a['job'],
                           title=a['title'],
                           text=a['text'],
                           start_date=start,
                           end_date=end)
        s.add(ad)

    s.commit()


# clear old day/count match/count info
def update_database():
    add_new_advertisements()
    s = Session()
    matches = s.query(Match)
    days = s.query(Day)
    for m in matches: s.delete(m)
    for d in days: s.delete(d)
    s.commit()

    search_all_techwords()



# get techwords, and search each advertisement for them
# store the results to database
def search_all_techwords():
    s = Session()
    words = s.query(TechWord)
    ads = s.query(Advertisement)

    # expanding search_strings from their JSON encoding
    search_ready_words = []
    for tw in words:
        search_ready_tw = { "word": tw.word,
                          "search_strings": json.loads(tw.search_strings),
                          "id": tw.id }
        search_ready_words.append(search_ready_tw)
        #print "\n---", tw.word
        #for key in search_ready_tw['search_strings']: print key,

    results = {}

    for ad in ads:
        for tw in search_ready_words: results[tw['id']] = 0

        search_techwords_from_ad(ad.text, search_ready_words, results)
        print "etsitaan tech_wordit ilmoituksesta: %s" % ad.title
        #for key in results: print key, ':', results[key], ' ',
        #print ''

        store_results_for_all_dates(ad, results, s)

    s.commit()
