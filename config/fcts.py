# -*- coding: utf-8 -*-
import configparser
import sqlalchemy as db
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from db.model import *
import logging
from datetime import date, timedelta
import os
import glob
import pandas as pd


def config(config_cat, config_name):
    """ Return a config value from the configfile"""

    config = configparser.ConfigParser()
    config.read('config/config.ini')

    return config[config_cat][config_name]

### SET Home directory
os.chdir(config('home', 'home'))

class log_class():
    """ Logging class """

    def __init__(self):

        # load config settings from config file
        self.log_path = os.path.join(config('home', 'home'), config('log', 'log_path'))
        self.log_name = date.today().isoformat() + ".log"
        self.log_format = config('log', 'log_format')
        self.log_nb_day = int(config('log', 'log_nb_day'))

        # make sure log directory exists
        self.log_dir()

        # Setup log config
        logging.basicConfig(filename = os.path.join(self.log_path, self.log_name), \
        level = logging.INFO, \
        format = self.log_format, \
        filemode = 'a')

        self.logger = logging.getLogger()

        # delete old logs
        self.flush()


    def info(self, message):
        """ lvl info """
        self.logger.info(message)

    def warning(self, message):
        """ lvl warning """
        self.logger.warning(message)

    def error(self, message):
        """ lvl error """
        self.logger.error(message)

    def log_dir(self):
        """ check if log directory exists, if not, create it """
        if not os.path.isdir(self.log_path):
            os.mkdir(self.log_path)

    def flush(self):
        """ delete log files older than N days """

        # loop on log files
        for log_path in glob.glob(self.log_path + "*.log"):
            str_log_date = os.path.basename(log_path).replace(".log","")
            log_date = date.fromisoformat(str_log_date)
            delete_date = date.today() + timedelta(days=-self.log_nb_day)

            if log_date < delete_date:
                os.remove(log_path)
                self.logger.info(f"log {str_log_date}.log has been removed")


class database():
    """ easy manage flows with database """

    def __init__(self):

        # Load config settings
        self.user = config('database','user')
        self.password = config('database','password')
        self.server = config('database','server')
        self.port = config('database','port')
        self.database = config('database','database')
        self.engine = db.create_engine(f'mysql+pymysql://{self.user}:{self.password}@{self.server}:{self.port}/{self.database}', echo = True)
        self.log = log_class()
        self.session = ''
        self.activate_session()

    def create(self):
        """ create database following defined model """

        try:
            if not database_exists(self.engine.url):
                create_database(self.engine.url)
            Base.metadata.create_all(self.engine)
            self.log.info("database schema implemented")

        except Exception as e:
            self.log.error("database schema faild")
            self.log.error(e)

    def drop(self):

        """ drop database """
        os.system("mysql --user=root --password=root -e \"drop database dev\"")

    def activate_session(self):
        """ create a session for query """

        try:
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            self.log.info("database connected")

        except Exception as e:
            self.log.error("database connection faild")
            self.log.error(e)

def queryset_to_dataframe(queryset):
    """ from a queryset return a dataframe """
