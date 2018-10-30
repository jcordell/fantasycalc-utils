from config import LocalHostConfig as config
from pymongo import MongoClient
from datatypes.fantasy_league import fantasy_league_dtype
import urllib.parse


class MongoDB:
    def connect(self, database_url=None):
        if database_url is None:
            database_url = config.DATABASE_URL
        connection = MongoClient('ds219191.mlab.com', 19191)
        databasename = 'fantasycalc'
        self._db = connection[databasename]
        self._db.authenticate('jcordell', 'Usarocks12')
        # self._db = _client.database
        self._cache = {}

    def update_league_trades(self, trade_dtype_list):
        trades = self._db.tradesWithId
        trades_json = [trade.to_json() for trade in trade_dtype_list]
        # update or insert if not exist TODO: would prefer insert if not exists
        for trade in trades_json:
            if trade['_id'] is None:
                raise RuntimeError('Trade does not have an _id')

        try:
            # semi-hacky insert if not exists
            # ordered false will try all of them at once
            # if there is already a trade in the db it will throw an error, but other inserts are still attempted (ordered=false)
            trades.insert_many(trades_json, ordered=False)
        except Exception:
            # assume duplicate key error (which is expected if trade is already in db, don't want to duplicate)
            print('Error inserting many trades...probably duplicate key')
            pass

    def update_league_settings(self, league):
        league_settings = self._db.league_settings
        # put league settings in cache
        league_settings.insert_one(league.to_json())
        self._cache[league.league_id] = league.to_json()

    def get_league_settings(self, league_id):
        # already caching elsewhere...but can't hurt to do it here too?
        if league_id in self._cache:
            return self._cache[league_id]

        settings_collection = self._db.league_settings
        settings = settings_collection.find_one({"league_id": str(league_id)})
        # settings not found, still return None
        if settings is None:
            return None
        # convert back to league settings datatype object interface
        return fantasy_league_dtype(settings)

    def insert_rankings(self, season_rankings):
        rankings = self._db.rankings
        rankings.insert_one(season_rankings)

    def get_league_ids(self, site):
        league_settings = self._db.league_settings
        return league_settings.distinct('league_id')
