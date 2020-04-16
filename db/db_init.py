import configparser
import sqlalchemy as db
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import Table, Column, Integer, String, Date, Float,ForeignKey, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

if __name__ == '__main__':

    # Import db settings
    config = configparser.ConfigParser()
    config.read('../config/config.ini')
    user = config['database']['user']
    server = config['database']['server']
    port = config['database']['port']
    database = config['database']['database']

    # Create db if not exists
    engine = db.create_engine(f'mysql+pymysql://{user}@{server}:{port}/{database}', echo = True)
    if not database_exists(engine.url):
        create_database(engine.url)

    Session = sessionmaker(bind=engine)
    Base = declarative_base()

    # Model
    class sector(Base):
        __tablename__ = 'sector'
        sector_id = Column('sector_id', Integer, primary_key = True)
        sector_nom = Column('sector_nom', String(100),nullable=False)
        sector_start_d = Column('sector_start_d', Date)
        sector_end_d = Column('sector_end_d', Date)

    def __init__(self, sector_id, sector_nom, sector_start_d, sector_end_d):
        self.sector_id = sector_id
        self.sector_nom = sector_nom
        self.sector_start_d = sector_start_d
        self.sector_end_d = sector_end_d

    class portfolio(Base):
        __tablename__ = 'portfolio'
        port_id = Column('port_id', Integer, primary_key = True)
        port_nom = Column('port_nom', String(100),nullable=False)
        port_date_d = Column('port_date_d', Date)
        port_date_f = Column('port_date_f', Date)

        def __init__(self, port_id, port_nom, port_date_d, port_date_f):
            self.port_id = port_id
            self.port_nom = port_nom
            self.port_date_d = port_date_d
            self.port_date_f = port_date_f

    class ref(Base):
        __tablename__ = 'ref'
        ref_id = Column('ref_id', Integer, primary_key = True)
        ref_nom = Column('ref_nom', String(100),nullable=False)
        ref_isin = Column('ref_isin', String(14),nullable=False)
        ref_url = Column('ref_url', String(40),nullable=False)
        ref_sector_id = Column('ref_sector_id', Integer, ForeignKey("sector.sector_id"), default=1)
        ref_start_d = Column('ref_start_d', Date)
        ref_end_d = Column('ref_end_d', Date)

        def __init__(self, ref_id, ref_nom, ref_isin, ref_url, ref_sector_id, ref_start_d, ref_end_d):
            self.ref_id = ref_id
            self.ref_nom = ref_nom
            self.ref_isin = ref_isin
            self.ref_url = ref_url
            self.ref_sector_id = ref_sector_id
            self.ref_start_d = ref_start_d
            self.ref_end_d = ref_end_d

    class data(Base):
        __tablename__ = 'data'
        data_id = Column('data_id', Integer, primary_key = True)
        data_ref_id = Column('data_ref_id', Integer, ForeignKey("ref.ref_id"),nullable=False)
        data_ouverture = Column('data_ouverture', Float(3), nullable=False)
        data_fermeture = Column('data_fermeture', Float(3), nullable=False)
        data_haut = Column('data_haut', Float(3), nullable=False)
        data_bas = Column('data_bas', Float(3), nullable=False)
        data_volume = Column('data_volume', Integer, nullable=False)
        data_date = Column('data_date', Date)

        def __init__(self, data_id, data_ref_id, data_ouverture, data_fermeture, data_haut, data_bas, data_volume, data_date):
            self.data_id = data_id
            self.data_ref_id = data_ref_id
            self.data_ouverture = data_ouverture
            self.data_fermeture = data_fermeture
            self.data_haut = data_haut
            self.data_bas = data_bas
            self.data_volume = data_volume
            self.data_date = data_date

    class price(Base):
        __tablename__ = 'price'
        price_id = Column('price_id', Integer, primary_key = True)
        price_date = Column('price_date', Date)
        price_1 = Column('price_1', Float(3), nullable=True, default=0.0)

        def __init__(self, price_id, price_date, price_1):
            self.price_id = price_id
            self.price_date = price_date
            self.price_1 = price_1

    class transaction(Base):
        __tablename__ = 'transaction'
        tran_id = Column('tran_id', Integer, primary_key = True)
        tran_qty = Column('tran_qty', Float(3), nullable=False)
        tran_type = Column('tran_type', String(10), nullable=False)
        tran_price = Column('tran_price', Float(3), nullable=False)
        tran_ref_id = Column('tran_ref_id', Integer, ForeignKey("ref.ref_id"), nullable=False)
        tran_port_id = Column('tran_port_id', Integer, ForeignKey("portfolio.port_id"), nullable=False)
        tran_date = Column('tran_date', Date)
        tran_com = Column('tran_com', String(100))

        def __init__(self, tran_id, tran_qty, tran_type, tran_price, tran_ref_id, tran_port_id, tran_date, tran_com):
            self.tran_id = tran_id
            self.tran_qty = tran_qty
            self.tran_type = tran_type
            self.tran_price = tran_price
            self.tran_ref_id = tran_ref_id
            self.tran_port_id = tran_port_id
            self.tran_date = tran_date
            self.tran_com = tran_com


    class valo(Base):
        __tablename__ = 'valo'
        valo_id = Column('valo_id', Integer, primary_key = True)
        valo_port_id = Column('valo_port_id', Integer, ForeignKey("portfolio.port_id"), nullable=False)
        valo_valo = Column('valo_valo', Float(3), nullable=False)
        valo_flow = Column('valo_flow', Float(3), nullable=False)
        valo_date = Column('valo_date', Date)

        def __init__(self, valo_id, valo_port_id, valo_valo, valo_flow, valo_date):
            self.valo_id = valo_id
            self.valo_port_id = valo_port_id
            self.valo_valo = valo_valo
            self.valo_flow = valo_flow
            self.valo_date = valo_date

    class weight(Base):
        __tablename__ = 'weight'
        weight_id = Column('weight_id', Integer, primary_key = True)
        weight_port_id = Column('weight_port_id', Integer, ForeignKey("portfolio.port_id"), nullable=False)
        weight_weight = Column('weight_weight', Float(3), nullable=False)
        weight_date =Column('weight_date', Date)

        def __init__(self, weight_id, weight_port_id, weight_weight, weight_date):
            self.weight_id = weight_id
            self.weight_port_id = weight_port_id
            self.weight_weight = weight_weight
            self.weight_date = weight_date

    Base.metadata.create_all(engine)
