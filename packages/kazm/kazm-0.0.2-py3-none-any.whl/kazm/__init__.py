import configparser
import os

settings = configparser.ConfigParser()
settings_path = os.path.join(os.path.dirname(__file__), "settings.ini")
settings.read(settings_path)