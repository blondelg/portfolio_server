# -*- coding: utf-8 -*-
from db.model import *
from config.fcts import *
from mining.p_yh import *
from mining.p_brsm import *

""" Module which holds all SQL queries used for the process """

def orm_query_to_dataframe(qry):
    """ from an SQLAlchemy query return a dataframe """
    return pd.read_sql(qry.statement, qry.session.bind, index_col='id')

class mref():

    """ manage ref methods """

    def __init__(self, ref_scope=None):
        self.log = log_class()
        self.scope = ref_scope
        self.id = []
        self.url = []
        self.target = "https://www.boursorama.com/cours/{url}"
        self.session = database().session
        self.dico = {} # key = ref id, value = ref_url

    def get_url(self, source_id):

        """ build the dict[ref_id] = url depending on the selected data source """

        # id scope not defined during init
        if self.scope is None:
            qry = self.session.query(ref,source).with_entities(ref.id, source.sou_url) \
            .filter(ref.id == source.sou_ref_id) \
            .filter(source.sou_source_ref_id == 1) \
            .filter_by(ref_end_d = None)

            df = orm_query_to_dataframe(qry)
            self.dico = df[df.columns[0]].to_dict()

        else:
            qry = self.session.query(ref,source).with_entities(ref.id, source.sou_url) \
            .filter(ref.id == source.sou_ref_id) \
            .filter(source.sou_source_ref_id == 1) \
            .filter(ref.id.in_(self.scope)) \
            .filter_by(ref_end_d = None)

            df = orm_query_to_dataframe(qry)
            self.dico = df[df.columns[0]].to_dict()

    def insert(self, ref_nom, ref_isin, ref_url, ref_sector_id=None):

        """ insert a new record in ref model """
        temp_ref = data(ref_nom = ref_nom, \
        ref_isin = ref_isin,\
        ref_url = ref_url,\
        ref_start_d = date.today().isoformat())

        self.session.add(temp_data)
        self.session.commit()


    def get_from_id(self, id):

        """ retrun record from a given id """

        return orm_query_to_dataframe(self.session.query(ref).filter_by(id = id))

    def update(self,):

        """ update if exists, else insert """

        pass

    def update_isin(self):

        """ update ISIN """

        for id, url in self.dico.items():
            t_isin = html_parser_metadata(url).isin
            if t_isin:
                self.session.query(ref).filter_by(id = id).update({'ref_isin': t_isin})
                self.session.commit()





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
            for row in html_parser_data_last(self.target + url).return_df().iterrows():

                if self.record_exists(id, row[1]["date"]) is False:
                    self.insert(id, row[1]["date"], row[1]["close"], row[1]["open"], row[1]["max"], row[1]["min"], row[1]["vol"])

    def load_histo(self, start_d, end_d):

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
        qry = self.session.query(data)
        df_data = orm_query_to_dataframe(qry)

        # build key from ref_id and date
        df_data["key"] = df_data["data_ref_id"].astype(str) + "#" + df_data["data_date"].astype(str)
        price_scope = df_data[~df_data["key"].isin(self.scope_price)]
        price_scope["price"] = (price_scope["data_haut"] + price_scope["data_bas"]) / 2
        price_scope["price"] = price_scope["price"].round(2)

        for row in price_scope.iterrows():
            self.insert(row[1].data_ref_id, row[1].data_date, row[1].price)

    def price_to_df(self):

        """ return a dataframe with ref in columns and dates in lines """

        return pd.pivot_table(df, values='price', index=['price_date'],columns=['price_ref_id'])


    def build_scope(self):

        """ create a list[ref_id # data_date] """

        for line in self.session.query(price).with_entities(price.price_ref_id, price.price_date):
            self.scope_price.append(str(line[0]) + "#" + str(line[1]))
