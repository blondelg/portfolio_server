# -*- coding: utf-8 -*-
import urllib
from urllib import request
from html.parser import HTMLParser
from db.qry import *

class html_parser_metadata(HTMLParser, object):

    """ parser to get metadata """

    def __init__(self, url):
        HTMLParser.__init__(self)
        self.url = url
        self.flag_isin = False
        self.isin = ''
        self.htlm = ''
        self.target = "https://www.boursorama.com"
        self.load_htlm(self.target + url)
        self.feed(self.html)


    def handle_starttag(self, tag, attrs):
        if "c-faceplate__isin" in str(attrs) and tag == 'h2':
            self.flag_isin = True

    def handle_data(self, data):
        if self.flag_isin:
            self.flag_isin = False
            self.isin = data.split(" ")[0].strip()


    def load_htlm(self,url):

        """ load raw HTML """

        with urllib.request.urlopen(url) as response:
            self.html = response.read().decode("utf-8")





class html_parser_data_last(HTMLParser, object):

    """ parser to get market data of a stock """

    def __init__(self, url):
        HTMLParser.__init__(self)
        self.url = url
        self.flag_histo = False
        self.flag_table = False
        self.flag_isin = False
        self.raw_list = ['date']
        self.htlm = ''
        self.target = "https://www.boursorama.com"
        self.load_htlm(self.target + url)
        self.feed(self.html)


    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.flag_table = True

        if "c-faceplate__isin" in str(attrs) and tag == 'h2':
            self.flag_isin = True

    def handle_endtag(self, tag):
        if tag == 'table':
            self.flag_table = False
            self.flag_histo = False

    def handle_data(self, data):
        if "HISTORIQUE 5 JOURS" in data.upper():
            self.flag_histo = True

        if self.flag_table and self.flag_histo:
            t_data = data.strip().replace("\n","")

            if t_data != "":
                self.raw_list.append(t_data)

        if self.flag_isin:
            self.flag_isin = False
            self.isin = data.split(" ")[0].strip()

    def return_df(self):

        """ return a dataframe with the 5 last days """

        head = ['date', 'close', 'open', 'max', 'min', 'vol']
        df_list = []
        temp = []
        count = 0
        for e in self.raw_list:
            temp.append(e)
            if count < self.nb_date():
                count += 1
            else:
                df_list.append(temp)
                temp = []
                count = 0

        df = pd.DataFrame(df_list).transpose()
        df = df.rename(columns=df.iloc[0])
        df = df.drop(0)
        df["date"] = df["date"].apply(lambda x: self.smart_date(x))
        df = df.drop('Var.', axis=1)
        df.columns = head
        df["close"] = df["close"].astype("float")
        df["open"] = df["open"].astype("float")
        df["max"] = df["max"].astype("float")
        df["min"] = df["min"].astype("float")
        df["vol"] = df["vol"].apply(lambda x: x.replace(" ",""))
        df["vol"] = df["vol"].astype("int")

        # remove today's date
        df = df[~df["date"].isin([date.today().isoformat()])]

        return df


    def smart_date(self, input_date):

        """ from a day and a month, give the right date """

        day = int(input_date[0:2])
        month = int(input_date[3:5])

        if date.today().month == 1 and month == 12:
            return date(date.today().year - 1,month, day).isoformat()
        else:
            return date(date.today().year,month, day).isoformat()

    def load_htlm(self,url):

        """ load raw HTML """

        with urllib.request.urlopen(url) as response:
            self.html = response.read().decode("utf-8")

    def nb_date(self):

        """ return how many dates there is in raw list """

        return int((len(self.raw_list) - 7)/7)


class html_parser_data_1Y(HTMLParser, object):

    """ parser to get historical market data of a stock """

    def __init__(self, url, start_d):
        HTMLParser.__init__(self)
        self.url = url.replace("/", "")
        self.start_d = start_d.replace("-", "/")
        self.nb_page = 1
        self.flag_page = False
        self.flag_page_loop = True
        self.flag_data = False
        self.raw_list = []
        self.htlm = ''
        self.target = "https://www.boursorama.com/_formulaire-periode/page-{page}?symbol={ref_url}&historic_search[startDate]={start_d}&historic_search[duration]=1Y&historic_search[period]=1&orderBy=date&orderAsc=1"
        self.load_htlm()
        self.feed(self.html)
        self.get_data()


    def handle_starttag(self, tag, attrs):
        # detect pagination data
        if "c-pagination__content" in str(attrs) and self.flag_page_loop:
            self.flag_page = True
        elif tag == "td":
            self.flag_data = True

    def handle_endtag(self, tag):
        # detect pagination data
        if tag and tag == "span" and self.flag_page_loop:
            self.flag_page = False
        elif tag == "td":
            self.flag_data = False

    def handle_data(self, data):
        # detect pagination data
        if self.flag_page and self.flag_page_loop:
            try:
                self.nb_page = int(data)
            except:
                pass

        elif self.flag_data == True:
            self.raw_list.append(data.strip().replace("\n",""))


    def load_htlm(self, url=None):

        """ load raw HTML """
        if url is None:
            with urllib.request.urlopen(self.target.format(page = "1", ref_url = self.url, start_d = self.start_d)) as response:
                self.html = response.read().decode("utf-8")
        else:
            with urllib.request.urlopen(url) as response:
                self.html = response.read().decode("utf-8")


    def get_data(self):

        """ loop over pages and grab datas """
        self.flag_page_loop = False
        for i in range(1, self.nb_page + 1):
            self.load_htlm(self.target.format(page = str(i), ref_url = self.url, start_d = self.start_d))
            self.feed(self.html)
