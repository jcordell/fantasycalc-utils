from abc import ABC, abstractmethod

class FantasySiteApi(ABC):

    @abstractmethod
    def get_valid_leagues(self, fast_search=True):
        '''
        Gets array of league_ids which can be searched
        fast_search if to check every league or only ones with trades in them
        :param fast_search: boolean on if only need trades for fast
        :return: list of valid league ids
        '''
        pass

    @abstractmethod
    def get_league_trades(self, league_id):
        '''
        :param league_id: league_id of league to gather trades from
        :return: array of trades in the trade_datatype format
        '''
        pass

    @abstractmethod
    def get_settings(self, league_id):
        '''
        Gets all league settings which we want to collect
        :param league_id: league_id to gather settings from
        :return: array or dict? of league settings
        '''
        pass