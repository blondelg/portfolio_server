# -*- coding: utf-8 -*-
import urllib
from urllib import request
from html.parser import HTMLParser
from db.qry import *

class html_parser_data_last(HTMLParser, object):

    """ parser to get market data of a stock """

    def __init__(self, url):
        HTMLParser.__init__(self)
        self.url = url
        self.flag_histo = False
        self.flag_table = False
        self.raw_list = ['date']
        self.htlm = ''
        self.load_htlm(url)
        self.feed(self.html)


    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.flag_table = True

    def handle_endtag(self, tag):
        if tag == 'table':
            self.flag_table = False
            self.flag_histo = False

    def handle_data(self, data):
        if "HISTORIQUE 5 JOURS" in data.upper():
            self.flag_histo = True
        if self.flag_table == True and self.flag_histo == True:
            t_data = data.strip().replace("\n","")
            if t_data != "":
                self.raw_list.append(t_data)

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

        print("DEBUG", input_date)
        print("DEBUG", self.url)

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
