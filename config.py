class LocalHostConfig:
    APP_NAME = 'local'
    DATABASE_TYPE = 'mongodb'
    DATABASE_URL = 'localhost'
    UPDATE_TRADES = True
    UPDATE_SETTINGS = False
    SITES = ['fleaflicker']  # ['mfl', 'ESPN', 'fleaflicker']
    YEAR = 2019


class MLabConfig:
    APP_NAME = 'mlab'
    DATABASE_TYPE = 'mongodb'
    DATABASE_URL = 'mongodb://jcordell:Usarocks12@ds219191.mlab.com:19191/fantasycalc'
    UPDATE_TRADES = True
    UPDATE_SETTINGS = False
    SITES = ['mfl']
    YEAR = 2018


class TestConfig:
    APP_NAME = 'local'
    DATABASE_TYPE = 'mongodb'
    DATABASE_URL = 'localhost'
    year = 2018
