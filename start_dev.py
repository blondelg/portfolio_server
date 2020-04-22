#!/home/geoffroy/Documents/1_projets_persos/21_portfolio/venv/bin/python
# -*- coding: utf-8 -*-
from config.fcts import *
from db.qry import *
import urllib
from urllib import request
from html.parser import HTMLParser
import pymysql
import os
import re

# 1 Deploy database
##################################################################
database().drop()
database().create()
# create source_ref
db=database()
temp_ref = source_ref(rsou_nom = 'boursorama')
db.session.add(temp_ref)
db.session.commit()
temp_ref = source_ref(rsou_nom = 'yahoo')
db.session.add(temp_ref)
db.session.commit()

# 2 load ref
##################################################################
# STEP 1: define ref parser and load index links and names
link = []
title = []

class html_parser_ref(HTMLParser):

    """ from an index list page, mine stock name and link"""

    def __init__(self):
        """ add new classvariables """
        HTMLParser.__init__(self)
        self.link = []
        self.title = []
        self.test_link = dict()

    def handle_starttag(self, tag, attrs):
        self.temp_attrs = attrs
        for attr in attrs:
            if attr[1] == 'c-link   c-link--animated / o-ellipsis' and self.temp_attrs[0][1] not in self.test_link:
                link.append(self.temp_attrs[0][1])
                title.append(self.temp_attrs[1][1].replace('\'',''))
                self.test_link[self.temp_attrs[0][1]] = 1

# List of web pages where index composition are store
url_cac40 = []
url_cac40.append('https://www.boursorama.com/bourse/actions/cotations/?quotation_az_filter%5Bmarket%5D=1rPCAC&quotation_az_filter%5Bletter%5D=&quotation_az_filter%5Bfilter%5D=')
url_cac40.append('https://www.boursorama.com/bourse/actions/cotations/page-2?quotation_az_filter%5Bmarket%5D=1rPCAC&quotation_az_filter%5Bletter%5D=&quotation_az_filter%5Bfilter%5D=')

# define parser object from class
parser = html_parser_ref()

# STEP 2: loop on url_cac40 urls to get data and parse
for url in url_cac40:
    resp = request.urlopen(url)
    data = resp.read()
    html = data.decode('latin-1').encode('utf-8').decode('utf-8')
    parser.feed(html)

# STEP 3: upload title and urls into db
# connect and feed database
db = pymysql.Connection("localhost","root","root","dev")
cursor = db.cursor()
temp_query = ''

# load data into ref
for i in range(len(title)):
    # populate ref
    temp_query = 'INSERT INTO ref (ref_nom, ref_start_d) VALUES (\'{}\', DATE(SYSDATE()));'.format(title[i])
    print(temp_query)
    cursor.execute(temp_query)
    db.commit()

    # populate source
    temp_query = 'INSERT INTO source (sou_ref_id, sou_source_ref_id, sou_url) VALUES (\'{}\',1,\'{}\' );'.format(i+1, link[i].replace("/","").replace("cours",""))
    print(temp_query)
    cursor.execute(temp_query)
    db.commit()



    sou_ref_id = Column('sou_ref_id', Integer, ForeignKey("ref.id"),nullable=False)
    sou_source_ref_id = Column('sou_source_ref_id', Integer, ForeignKey("source_ref.id"),nullable=False)
    sou_url = Column('ref_url', String(40),nullable=False)



# commit and close
db.commit()
db.close()

# 3 Load isin
##################################################################
a=mref()
a.get_url(1)
a.update_isin()

# 4 load source for yahoo
#################################################################
class html_parser_yahoo(HTMLParser, object):

    """ parser to get market data of a stock """

    def __init__(self, isin):
        HTMLParser.__init__(self)
        self.flag = False
        self.flag_link = False
        self.url = ''
        self.target = "https://fr.search.yahoo.com/search?p={isin}+yahoo+quote".format(isin = isin)
        self.load_htlm()
        self.feed(self.html)

    def handle_starttag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        if re.match(r"(.)*/(.)*\.PA", data) is not None:
            self.url = data.replace("/","")
            return



    def load_htlm(self):

        """ load raw HTML """

        with urllib.request.urlopen(self.target) as response:
            self.html = response.read().decode("utf-8")


#
db=database()
for line in db.session.query(ref).with_entities(ref.id, ref.ref_isin):
    print(line)
    temp_data = source(sou_ref_id = line[0], \
    sou_source_ref_id = 2,\
    sou_url = html_parser_yahoo(line[1]).url)

    db.session.add(temp_data)
    db.session.commit()
