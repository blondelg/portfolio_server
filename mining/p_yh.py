# -*- coding: utf-8 -*-
import urllib
from urllib import request
from html.parser import HTMLParser
from db.qry import *
import re

class html_parser_url_from_isin(HTMLParser, object):

    """ get yahoo url from isin """

    def __init__(self, isin):
        HTMLParser.__init__(self)
        self.flag = False
        self.flag_link = False
        self.url = ''
        self.target = "https://fr.search.yahoo.com/search?p={isin}+yahoo+quote".format(isin = isin)
        self.load_htlm()
        self.feed(self.html)

    def handle_starttag(self, tag, attrs):
        try:
            if re.match(r"https:(.)*inance.yahoo.com/quote(.)*", dict(attrs)["href"]) is not None:
                if len(dict(attrs)["href"].split("/")[-2]) < 8:
                    self.url = dict(attrs)["href"].split("/")[-2]
                    return
        except:
            pass

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        pass


    def load_htlm(self):

        """ load raw HTML """

        with urllib.request.urlopen(self.target) as response:
            self.html = response.read().decode("utf-8")
