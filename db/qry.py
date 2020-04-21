# -*- coding: utf-8 -*-
from db.model import *
from config.fcts import *
from mining.parser import *

""" Module which holds all SQL queries used for the process """

class mref():

    """ manage ref methods """

    def __init__(self, ref_scope=None):
        self.log = log_class()
        self.scope = ref_scope
        self.id = []
        self.url = []
        self.session = database().session
        self.dico = {}
        self.get_active()

    def get_active(self):

        """ get active id, url """

        # id scope not defined during init
        if self.scope is None:
            for line in self.session.query(ref).with_entities(ref.id, ref.ref_url).filter_by(ref_end_d = None):
                self.id.append(line[0])
                self.url.append(line[1])
                self.dico[line[0]] = line[1]

        else:
            for line in self.session.query(ref).with_entities(ref.id, ref.ref_url).filter_by(ref_end_d = None).filter(ref.id.in_(self.scope)):
                self.id.append(line[0])
                self.url.append(line[1])
                self.dico[line[0]] = line[1]

    def insert(self, ref_nom, ref_isin, ref_url, ref_sector_id=None):

        """ insert a new record in ref model """
        temp_ref = data(ref_nom = ref_nom, \
        ref_isin = ref_isin,\
        ref_url = ref_url,\
        ref_start_d = date.today().isoformat())

        self.session.add(temp_data)
        self.session.commit()


    def update(self,):

        """ update existing record """

        pass

    def update_or_insert(self,):

        """ update if exists, else insert """

        pass

    def disable(self,):

        """ disable records from a given ref or ref list """

        pass


class mdata():

    """ manage data methods """

    def __init__(self):
        self.log = log_class()
        self.session = database().session

    def insert(self, ref_id, date, fermeture, ouverture, haut, bas, vol):

        """ insert a new record in data model """

        temp_data = data(data_ref_id = ref_id, \
        data_ouverture = ouverture,\
        data_fermeture = fermeture,\
        data_haut = haut,\
        data_bas = bas,\
        data_volume = vol,\
        data_date = date)

        self.session.add(temp_data)
        self.session.commit()


    def record_exists(self, ref_id, date):

        """ returne True if there is a record for a ref, a a date """

        if self.session.query(data).filter_by(data_ref_id = ref_id, data_date = date).count() == 0:
            return False
        else:
            return True

    def load_last(self):

        """ load last days for active scope """

        for id, url in mref().dico.items():
            for row in html_parser_data_last("https://www.boursorama.com" + url).return_df().iterrows():

                if self.record_exists(id, row[1]["date"]) is False:
                    self.insert(id, row[1]["date"], row[1]["close"], row[1]["open"], row[1]["max"], row[1]["min"], row[1]["vol"])

    def load_histo(self):

        """ load historical data for active scope """
        pass






class mprice():

    """ manage price methods """

    def __init__(self):
        self.session = database().session
        self.scope_price = []
        self.build_scope()

    def insert(self,price_ref_id, price_date, price_price):

        """ insert a new record in data model """
        temp_data = price(price_ref_id = price_ref_id, \
        price_date = price_date, \
        price_price = price_price)

        self.session.add(temp_data)
        self.session.commit()

    def update_from_data(self):

        """ update all price from data if record is not existing """

        # load data into a dataframe
        output_cursor = self.session.query(data)
        df_data = pd.read_sql(output_cursor.statement, output_cursor.session.bind, index_col='id')

        # build key from ref_id and date
        df_data["key"] = df_data["data_ref_id"].astype(str) + "#" + df_data["data_date"].astype(str)
        price_scope = df_data[~df_data["key"].isin(self.scope_price)]
        price_scope["price"] = (price_scope["data_haut"] + price_scope["data_bas"]) / 2
        price_scope["price"] = price_scope["price"].round(2)

        for row in price_scope.iterrows():
            #print(row[1].data_ref_id, row[1].data_date, row[1].price)
            self.insert(row[1].data_ref_id, row[1].data_date, row[1].price)

    def price_to_df(self):

        """ return a dataframe with ref in columns and dates in lines """

        return pd.pivot_table(df, values='price', index=['price_date'],columns=['price_ref_id'])


    def build_scope(self):

        """ create a list[ref_id # data_date] """

        for line in self.session.query(price).with_entities(price.price_ref_id, price.price_date):
            self.scope_price.append(str(line[0]) + "#" + str(line[1]))
