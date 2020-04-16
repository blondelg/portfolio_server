import configparser
import sqlalchemy as db
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import Table, Column, Integer, String, Date, Float,ForeignKey, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from db_schema import *

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
    Base.metadata.create_all(engine)
