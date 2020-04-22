# -*- coding: utf-8 -*-
from sqlalchemy import Table, Column, Integer, String, Date, Float,ForeignKey, MetaData
from sqlalchemy.ext.declarative import declarative_base

# Model
Base = declarative_base()

class sector(Base):
    __tablename__ = 'sector'
    __table_args__ = {'comment': 'sector list'}
    id = Column('id', Integer, primary_key = True)
    sector_nom = Column('sector_nom', String(100),nullable=False)
    sector_start_d = Column('sector_start_d', Date)
    sector_end_d = Column('sector_end_d', Date)

    def __repr__(self):
        return f"<sector(sector_nom='{self.sector_nom}', \
        sector_start_d='{self.sector_start_d}', \
        sector_end_d='{self.sector_end_d}')>"

class portfolio(Base):
    __tablename__ = 'portfolio'
    __table_args__ = {'comment': 'portfolio list'}
    id = Column('id', Integer, primary_key = True)
    port_nom = Column('port_nom', String(100),nullable=False)
    port_date_d = Column('port_date_d', Date)
    port_date_f = Column('port_date_f', Date)

    def __repr__(self):
        return f"<portfolio(port_nom='{self.port_nom}', \
        port_date_d='{self.port_date_d}', \
        port_date_f='{self.port_date_f}')>"

class ref(Base):
    __tablename__ = 'ref'
    __table_args__ = {'comment': 'asset scope'}
    id = Column('id', Integer, primary_key = True)
    ref_nom = Column('ref_nom', String(100),nullable=False)
    ref_isin = Column('ref_isin', String(14),nullable=True)
    # ref_url = Column('ref_url', String(40),nullable=False)
    # ref_id_yahoo = Column('ref_id_yahoo', String(40),nullable=True)
    ref_sector_id = Column('ref_sector_id', Integer, ForeignKey("sector.id"), default=1)
    ref_start_d = Column('ref_start_d', Date)
    ref_end_d = Column('ref_end_d', Date)

    def __repr__(self):
        return f"<ref(ref_nom='{self.ref_nom}', \
        ref_isin='{self.ref_isin}', \
        ref_url='{self.ref_url}', \
        ref_id_yahoo='{self.ref_id_yahoo}', \
        ref_sector_id='{self.ref_sector_id}', \
        ref_start_d='{self.ref_start_d}', \
        ref_end_d='{self.ref_end_d}')>"

class source(Base):
    __tablename__ = 'source'
    __table_args__ = {'comment': 'list of url in data sources'}
    id = Column('id', Integer, primary_key = True)
    sou_ref_id = Column('sou_ref_id', Integer, ForeignKey("ref.id"),nullable=False)
    sou_source_ref_id = Column('sou_source_ref_id', Integer, ForeignKey("source_ref.id"),nullable=False)
    sou_url = Column('sou_url', String(40),nullable=False)

    def __repr__(self):
        return f"<ref(sou_ref_id='{self.sou_ref_id}', \
        sou_url='{self.sou_url}')>"

class source_ref(Base):
    __tablename__ = 'source_ref'
    __table_args__ = {'comment': 'list reference of each source'}
    id = Column('id', Integer, primary_key = True)
    rsou_nom = Column('rsou_nom', String(40),nullable=False)

    def __repr__(self):
        return f"<source_ref(rsou_nom='{self.rsou_nom}')>"

class data(Base):
    __tablename__ = 'data'
    __table_args__ = {'comment': 'raw data'}
    id = Column('id', Integer, primary_key = True)
    data_ref_id = Column('data_ref_id', Integer, ForeignKey("ref.id"),nullable=False)
    data_ouverture = Column('data_ouverture', Float(3), nullable=False)
    data_fermeture = Column('data_fermeture', Float(3), nullable=False)
    data_haut = Column('data_haut', Float(3), nullable=False)
    data_bas = Column('data_bas', Float(3), nullable=False)
    data_volume = Column('data_volume', Integer, nullable=False)
    data_date = Column('data_date', Date)

    def __repr__(self):
        return f"<data(data_ref_id='{self.data_ref_id}', \
        data_ouverture='{self.data_ouverture}', \
        data_fermeture='{self.data_fermeture}', \
        data_haut='{self.data_haut}', \
        data_bas='{self.data_bas}', \
        data_volume='{self.data_volume}', \
        data_date='{self.data_date}')>"

class price(Base):
    __tablename__ = 'price'
    __table_args__ = {'comment': 'calculated price for each asset'}
    id = Column('id', Integer, primary_key = True)
    price_ref_id = Column('price_ref_id', Integer, ForeignKey("ref.id"),nullable=False)
    price_date = Column('price_date', Date)
    price_price = Column('price_price', Float(3), nullable=True, default=0.0)

    def __repr__(self):
        return f"<price(price_ref_id='{self.price_ref_id}', \
        price(price_date='{self.price_date}', \
        price_price='{self.price_price}')>"

class transaction(Base):
    __tablename__ = 'transaction'
    __table_args__ = {'comment': 'list of transaction'}
    id = Column('id', Integer, primary_key = True)
    tran_qty = Column('tran_qty', Float(3), nullable=False)
    tran_type = Column('tran_type', String(10), nullable=False)
    tran_price = Column('tran_price', Float(3), nullable=False)
    tran_ref_id = Column('tran_ref_id', Integer, ForeignKey("ref.id"), nullable=False)
    tran_port_id = Column('tran_port_id', Integer, ForeignKey("portfolio.id"), nullable=False)
    tran_date = Column('tran_date', Date)
    tran_com = Column('tran_com', String(100))

    def __repr__(self):
        return f"<transaction(tran_qty='{self.tran_qty}', \
        tran_type='{self.tran_type}', \
        tran_price='{self.tran_price}', \
        tran_ref_id='{self.tran_ref_id}', \
        tran_port_id='{self.tran_port_id}', \
        tran_date='{self.tran_date}', \
        tran_com='{self.tran_com}')>"

class valo(Base):
    __tablename__ = 'valo'
    __table_args__ = {'comment': 'valorisation for each portfolio'}
    id = Column('id', Integer, primary_key = True)
    valo_port_id = Column('valo_port_id', Integer, ForeignKey("portfolio.id"), nullable=False)
    valo_valo = Column('valo_valo', Float(3), nullable=False)
    valo_flow = Column('valo_flow', Float(3), nullable=False)
    valo_date = Column('valo_date', Date)

    def __repr__(self):
        return f"<valo(valo_port_id='{self.valo_port_id}', \
        valo_valo='{self.valo_valo}', \
        valo_flow='{self.valo_flow}', \
        valo_date='{self.valo_date}')>"

class weight(Base):
    __tablename__ = 'weight'
    __table_args__ = {'comment': 'asset weight within portfolio'}
    id = Column('id', Integer, primary_key = True)
    weight_ref_id = Column('weight_ref_id', Integer, ForeignKey("ref.id"),nullable=False)
    weight_port_id = Column('weight_port_id', Integer, ForeignKey("portfolio.id"), nullable=False)
    weight_weight = Column('weight_weight', Float(3), nullable=False)
    weight_date =Column('weight_date', Date)

    def __repr__(self):
        return f"<weight(weight_port_id='{self.weight_port_id}', \
        weight_weight='{self.weight_weight}', \
        weight_date='{self.weight_date}')>"
