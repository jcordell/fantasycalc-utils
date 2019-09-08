import json
import requests
import re
from bs4 import BeautifulSoup
from datatypes.fantasy_league import fantasy_league_dtype
from datatypes.trade import trade_dtype
from services.apis.mfl_api import mfl_api
from services.fantasysites.FantasySiteService import FantasySiteService
import sys
sys.path.append('/Users/jkc023/Documents/homeprojects/fantasycalc-utils/')


class MFLService(FantasySiteService):
    def __init__(self, year):
        self.year = year
        self.mfl_api = mfl_api()
        self.id_converter = self.__get_converter__()
        self._cache = {}

    '''
    fast_search would only search for leagues that already have trades in db
    setting to false would search for all dynasty leagues
    '''

    def get_valid_leagues(self, fast_search=True):
        league_page = self.mfl_api.get_league_id_page()
        soup = BeautifulSoup(league_page, 'html.parser')
        league_id_list = []
        for league in soup.find_all('a', href=True):
            league_string = re.escape(str(league))
            if 'Dynasty' in league_string:
                id = league_string.split("/")[5].split("\\")[0].split("\"")[0]
                league_id_list.append(id)
        return league_id_list

    def get_trades(self, league_id):
        # download the page from mfl
        trades = self.mfl_api.get_league_trades(league_id, self.year)

        # reformat to trade datatype
        new_trades = []

        # iterate over every trade in that league and convert to trade_dtypes
        if trades is not None:
            for trade in trades:
                try:
                    new_trade = __reformat_trade__(trade, league_id)
                    new_trade = self.convert_trade_ids_to_names(new_trade)
                    new_trades.append(new_trade)
                except Exception as e:
                    pass
                    # print(e)
        return new_trades

    def get_settings(self, league_id):
        if league_id in self._cache:
            return self._cache[league_id]
        else:
            league = fantasy_league_dtype()
            # MFL split league settings into 2 endpoints
            try:
                basic_settings = self.mfl_api.get_basic_settings(league_id)
                league.league_id = league_id
                league.site = 'mfl'
                league.num_teams = int(
                    basic_settings['league']['franchises']['count'])
                league.name = basic_settings['league']['name'].lstrip()

                # startings qbs formatted as '0-1'
                starting_qbs_string = basic_settings['league']['starters']['position'][0]['limit']
                league.num_qbs = int(starting_qbs_string.split('-')[-1])

                # get advanced settings(ppr)

                advanced_settings = self.mfl_api.get_advanced_settings(
                    league_id)
                parsed_advanced_settings = __parse_advanced_settings__(
                    advanced_settings)
                league.ppr = float(parsed_advanced_settings['ppr'])

                self._cache[league_id] = league

                return league
            except Exception as e:
                pass

    def convert_list(self, player_list, converter):
        for i in range(len(player_list)):
            if player_list[i] in converter:
                # remove a leading whitespace
                player_list[i] = converter[player_list[i]].lstrip()
            else:
                # don't want to add unconverted picks to our dictionary
                print('could not convert' + player_list[i])
                raise LookupError
        return player_list

    def convert_trade_ids_to_names(self, trade_dtype):
        try:
            trade_dtype.side1 = self.convert_list(
                trade_dtype.side1, self.id_converter)
            trade_dtype.side2 = self.convert_list(
                trade_dtype.side2, self.id_converter)
            trade_dtype.all_players = self.convert_list(
                trade_dtype.all_players, self.id_converter)
        except LookupError:
            raise LookupError
        return trade_dtype

    def __get_id_to_player_dict__(self):
        page = requests.get(
            "http://www63.myfantasyleague.com/2019/export?TYPE=players&L=11083&W=&JSON=1")
        players_json = json.loads(page.text)
        converter = {}
        for player in players_json['players']['player']:
            # convert from Doe, John to John Doe
            name_array = player['name'].split(",")
            converter[player['id']] = name_array[1] + " " + name_array[0]
        return converter

    def __make_id_to_draft_pick_converter__(self):
        '''
        current draft picks are formatted as DP_02_05 = 2018 Round 3 Pick 5
        future draft picks formmated as FP_0005_2018_2 
        where 0005 referes to the franchise id who originally owns the draft pick, 
        then the year and then the round 
        (in this case the rounds are the actual rounds, not one less).
        '''

        # (TODO) probably a really cool pythonic way to do this...whatever works for now
        pick_converter = {}
        # this year's picks
        for round_num in range(1, 10):
            for pick_num in range(1, 20):
                # if pick_num < 10:
                #     pick_num = '0' + str(pick_num)
                # else:
                converted_pick = str(
                    2019) + ' Round ' + str(round_num) + ' Pick ' + str(pick_num)
                pick_id = 'DP_' + str(round_num - 1) + '_' + str(pick_num - 1)
                pick_converter[pick_id] = converted_pick

        # future picks
        for round_num in range(1, 10):
            for year in range(2018, 2025):
                for team_num in range(0, 20):
                    if team_num < 10:
                        team_num = '000' + str(team_num)
                    else:
                        team_num = '00' + str(team_num)
                    converted_pick = str(year) + ' Round ' + str(round_num)
                    pick_id = 'FP_' + str(team_num) + '_' + \
                        str(year) + '_' + str(round_num)
                    pick_converter[pick_id] = converted_pick
        return pick_converter

    def __get_converter__(self):
        id_to_players = self.__get_id_to_player_dict__()
        id_to_draft_pick = self.__make_id_to_draft_pick_converter__()
        return {**id_to_players, **id_to_draft_pick}


def __reformat_trade__(trade, league_id):
    new_trade = trade_dtype()
    new_trade.league_id = league_id
    new_trade.fantasy_site = 'mfl'

    # formatted in strings seperated by commas, turn to list and remove last empty item
    new_trade.side1 = trade['franchise1_gave_up'].split(',')[:-1]
    new_trade.side2 = trade['franchise2_gave_up'].split(',')[:-1]
    new_trade.timestamp = int(trade['timestamp'])
    new_trade.all_players = new_trade.side1 + new_trade.side2
    return new_trade


def __parse_advanced_settings__(settings):
    ppr = 0

    for setting in settings['rules']['positionRules']:
        if isinstance(setting, dict):
            if 'WR' in setting['positions'].split('|'):
                for rule in setting['rule']:
                    if rule['event']['$t'] == 'CC':
                        ppr = rule['points']['$t'].split('*')[-1]

        elif isinstance(setting, str):
            if 'WR' in settings['rules']['positionRules']['positions'].split('|'):
                for rule in settings['rules']['positionRules']['rule']:
                    if rule['event']['$t'] == 'CC':
                        ppr = rule['points']['$t'].split('*')[-1]
            return {
                'ppr': ppr
            }
    return {
        'ppr': ppr
    }


# service = MFLService(2019)
# service.get_settings(35465)
# service.get_settings(10431)
