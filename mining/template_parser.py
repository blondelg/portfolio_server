import urllib
from urllib import request
from html.parser import HTMLParser
import pandas as pd

class html_parser(HTMLParser, object):

    """ parser to get market data of a stock """

    def __init__(self, arg):
        HTMLParser.__init__(self)
        self.flag = False
        self.raw_list = []
        self.target = '' # URL 
        self.load_htlm()
        self.feed(self.html)

    def handle_starttag(self, tag, attrs):
        print(tag, str(attrs))

    def handle_endtag(self, tag):
        print(tag)

    def handle_data(self, data):
        print(data)


    def load_htlm(self):

        """ load raw HTML """

        with urllib.request.urlopen(self.target) as response:
            self.html = response.read().decode("utf-8")
