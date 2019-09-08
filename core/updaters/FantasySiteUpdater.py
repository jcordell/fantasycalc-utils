from core.factory.DatabaseFactory import get_database
from core.factory.FantasySiteFactory import FantasySiteFactory
from tqdm import tqdm


class FantasySiteUpdater:
    def __init__(self, fantasy_site, year):
        site_factory = FantasySiteFactory()
        self.year = year

        self.fantasy_service = site_factory.get_site_api(fantasy_site, year)

        # connection to local/remote database
        self._db = get_database()
        self._db.connect()

        self._settings = {}

    '''
    returns settings datatype for specified league id

    first try to get settings from cache
    if settings aren't in cache, try to get from database
      - can skip getting from database if updating all
    if not in database, go out to api and download the trades
    '''

    def get_settings(self, league_id):
        if league_id in self._settings:
            return self._settings[league_id]

        settings = self._db.get_league_settings(league_id)
        if settings is None:
            settings = self.fantasy_service.get_settings(league_id)

        if settings is not None:
            self._settings[league_id] = settings
        return settings

    # gets valid leagues and updates
    def update_settings(self):
        league_ids = self.fantasy_service.get_valid_leagues()

        all_settings = []
        for league_id in league_ids:
            settings = self.fantasy_service.get_settings(league_id)
            if settings is not None:
                self._db.update_league_settings(settings)
                all_settings.append(settings)
        return all_settings

    # gets and updates trades for the fantasy site, sending to database and return trade objects
    def update_trades(self):
        league_ids = self.fantasy_service.get_valid_leagues()

        all_trades = []
        for league_id in tqdm(league_ids):
            try:
                settings = self.get_settings(league_id)
                if settings is None:
                    continue
                trades = self.fantasy_service.get_trades(league_id)

                # add settings object to each trade and create unique _id
                for trade in trades:
                    trade._id = str(trade.league_id) + '-' + \
                        str(trade.timestamp)
                    trade.league_settings = settings.to_json()

                if len(trades) > 0:
                    # update league settings in db
                    self._db.update_league_settings(settings)

                    self._db.update_league_trades(trades)
                    all_trades.append(trades)
            except Exception as e:
                print(e)
        return all_trades
