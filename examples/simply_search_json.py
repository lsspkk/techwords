#!/usr/bin/python

#
# run this example on web server that can run python script
#
# loads work advertisements and uses keywords from below to
# demonstrate search
#



# apache2:ssa python-tiedoston suorittamiseksi piti enabloida mod_cgid
# https://blog.tormix.com/%D0%B1%D0%B5%D0%B7-%D1%80%D1%83%D0%B1%D1%80%D0%B8%D0%BA%D0%B8/how-to-run-python-scripts-py-files-on-apache2-configuring-unix-apache2-servers/

import sys, json, operator, cgi, cgitb

from xml.sax.saxutils import escape

cgitb.enable()
print "Content-Type: text/html"
print ""
print "<html><head><style>body { font-size: 9px; } </style></head><body>"
print "<div style='display:block;float:right;width:300px'><pre>"

keywords = [ ['Angular', 'Angular2'],
    [' REST', ',REST'],
    ['JavaScript', 'JavaScripti'],
    ['Java', 'Javaa', 'Java-kehitt', 'Java-arkkitehti'],
    ['TypeScript', 'TypeScripti'],
    ['React'],
    ['Microsoft'],
    ['C#'],
    ['C++'],
    ['SQL', 'SQL-tietokannoista', 'SQL-tietokan'],
    ['Python'],
    ['AWS'],
    ['Azure'],
    ['.NET'],
    ['Heroku'],
    [' GIT'],
    ['CSS', ' SASS', ' LESS'],
    [' C ', ' C,'],
    ['Windows'],
    ['Linux'],
    ['Scrum'],
    ['Docker'],
    ['node.js', 'nodejs'],
    ['PHP'],
    ['html5'],
    ['jQuery'],
    ['jenkins'],
    [' qt']]

counters = []
for k in keywords:
    lowcase = []
    for i in k: lowcase.append(i.lower())
    counters.append({ 'skill': k[0], 'keywords': lowcase, 'count': 0 })

ads = {}
# Read JSON file
with open('../data/bar.json') as data_file:
    ads = json.load(data_file)


# etsii kaikki sanat
def find_keywords_all(text):
    words = text.split()
    for word in words:
        w = word.lower()
        for k in counters:
            for kw in k['keywords']:
                if w.startswith(kw):
                    k['count'] = k['count'] + 1

def find_keywords(text):
    tl = text.lower()
    for k in counters:
        for kw in k['keywords']:
            print "searching.." + kw,
            i = tl.find(kw)
            if i >= 0:
                print "found!:"
                print "-"*40
                print escape(tl[i-10:i+20])
                print "-"*40
                k['count'] = k['count'] + 1
                break
            else:
                print "not found"



def print_results(li):
    for k in li:
        print "%5d -- %s" % (k['count'], k['skill'])


for ad in ads.keys():
    find_keywords(ads[ad]['ilmoitus']['kuvaustekstiHTML'])

newlist = sorted(counters, key=operator.itemgetter('count'), reverse=True)

print "</pre></div>"
print "<div style='position:fixed;width:300px;top:20px;left:20px;'><pre>"

print "Ilmoituksia %s kpl" % (len(ads))
print_results(newlist)
print "</pre></div>"
print "</body></html>"
