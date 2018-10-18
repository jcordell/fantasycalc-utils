from config import LocalHostConfig as config
from pymongo import MongoClient


class MongoDB:
    def connect(self, database_url=None):
        if database_url is None:
            database_url = config.DATABASE_URL
        _client = MongoClient(database_url)
        self._db = _client.database
        self._cache = {}

    def update_league_trades(self, trade_dtype_list):
        trades = self._db.trades
        trades_json = [trade.to_json() for trade in trade_dtype_list]
        trades.insert_many(trades_json)

    def update_league_settings(self, league):
        league_settings = self._db.league_settings
        # put league settings in cache
        # league_settings.insert_one(league.to_json())

    def get_league_settings(self, leagueid):
        if leagueid in self._cache:
            return self._cache[leagueid]

    def insert_rankings(self, season_rankings):
        rankings = self._db.rankings
        rankings.insert_one(season_rankings)
