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

    # gets valid leagues and updates
    def update_settings(self):
        league_ids = self.fantasy_service.get_valid_leagues()

        all_settings = []
        for league_id in league_ids:
            settings = self.fantasy_service.get_settings(league_id)
            self._db.update_league_settings(settings)
            all_settings.append(settings)
        return all_settings

    # gets and updates trades for the fantasy site, sending to database and return trade objects
    def update_trades(self):
        league_ids = self.fantasy_service.get_valid_leagues()

        all_trades = []
        for league_id in tqdm(league_ids):
            try:
                settings = self.fantasy_service.get_settings(league_id)
                trades = self.fantasy_service.get_trades(league_id)
                if len(trades) > 0:
                    # update league settings in db
                    self._db.update_league_settings(settings)

                    self._db.update_league_trades(trades)
                    all_trades.append(trades)
            except Exception as e:
                print(e)
        return all_trades
