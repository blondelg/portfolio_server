import configparser
import logging
from datetime import date, timedelta
import os
import glob


def config(config_cat, config_name):
    """ Return a config value from the configfile"""

    config = configparser.ConfigParser()
    config.read('config.ini')
    
    return config[config_cat][config_name]

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

        for log_path in glob.glob(self.log_path + "*.log"):
            str_log_date = os.path.basename(log_path).replace(".log","")
            log_date = date.fromisoformat(str_log_date)
            delete_date = date.today() + timedelta(days=-self.log_nb_day)

            if log_date < delete_date:
                os.remove(log_path)
                self.logger.info(f"log {str_log_date}.log has been removed")
