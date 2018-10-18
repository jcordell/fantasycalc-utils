import sys
sys.path.append('/Users/jkc023/Documents/homeprojects/fantasycalc-utils/')
from services.fantasysites.FantasySiteService import FantasySiteService
from services.apis.mfl_api import mfl_api
from datatypes.trade import trade_dtype
from datatypes.fantasy_league import fantasy_league_dtype
from bs4 import BeautifulSoup
import re
import requests
import json


# class ESPNService(FantasySiteService):
#     def __init__(self, year):
#         self.year = year
#         self.mfl_api = mfl_api()
#         self.id_converter = self.__get_converter__()
#         self._cache = {}

#     '''
#     fast_search would only search for leagues that already have trades in db
#     setting to false would search for all dynasty leagues
#     '''

#     def get_valid_leagues(self, fast_search=True):
#         league_page = self.mfl_api.get_league_id_page()
#         soup = BeautifulSoup(league_page, 'html.parser')
#         league_id_list = []
#         for league in soup.find_all('a', href=True):
#             league_string = re.escape(str(league))
#             if 'Dynasty' in league_string:
#                 id = league_string.split("/")[5].split("\\")[0]
#                 league_id_list.append(id)
#         return league_id_list

#     def get_trades(self, league_id):
#         # download the page from mfl
#         trades = self.mfl_api.get_league_trades(league_id, self.year)

#         # reformat to trade datatype
#         new_trades = []

#         # iterate over every trade in that league and convert to trade_dtypes
#         if trades is not None:
#             for trade in trades:
#                 try:
#                     new_trade = __reformat_trade__(trade, league_id)
#                     new_trade = self.convert_trade_ids_to_names(new_trade)

#                     # get settings

#                     new_trade.league_settings = self.get_settings(
#                         league_id).to_json()
#                     new_trades.append(new_trade)
#                 except Exception as e:
#                     print(e)
#         return new_trades

#     def get_settings(self, league_id):
#         if league_id in self._cache:
#             return self._cache[league_id]
#         else:
#             league = fantasy_league_dtype()
#             # MFL split league settings into 2 endpoints
#             try:
#                 basic_settings = self.mfl_api.get_basic_settings(league_id)
#                 league.league_id = league_id
#                 league.site = 'mfl'
#                 league.num_teams = int(
#                     basic_settings['league']['franchises']['count'])
#                 league.name = basic_settings['league']['name'].lstrip()

#                 # startings qbs formatted as '0-1'
#                 starting_qbs_string = basic_settings['league']['starters']['position'][0]['limit']
#                 league.num_qbs = int(starting_qbs_string.split('-')[-1])

#                 # get advanced settings(ppr)

#                 advanced_settings = self.mfl_api.get_advanced_settings(
#                     league_id)
#                 parsed_advanced_settings = __parse_advanced_settings__(
#                     advanced_settings)
#                 league.ppr = float(parsed_advanced_settings['ppr'])

#                 self._cache[league_id] = league
#                 return league
#             except Exception as e:
#                 pass

#     def convert_list(self, player_list, converter):
#         for i in range(len(player_list)):
#             if player_list[i] in converter:
#                 # remove a leading whitespace
#                 player_list[i] = converter[player_list[i]].lstrip()
#             else:
#                 # don't want to add unconverted picks to our dictionary
#                 print('could not convert' + player_list[i])
#                 raise LookupError
#         return player_list

#     def convert_trade_ids_to_names(self, trade_dtype):
#         try:
#             trade_dtype.side1 = self.convert_list(
#                 trade_dtype.side1, self.id_converter)
#             trade_dtype.side2 = self.convert_list(
#                 trade_dtype.side2, self.id_converter)
#             trade_dtype.all_players = self.convert_list(
#                 trade_dtype.all_players, self.id_converter)
#         except LookupError:
#             raise LookupError
#         return trade_dtype

#     def __get_id_to_player_dict__(self):
#         page = requests.get(
#             "http://www63.myfantasyleague.com/2018/export?TYPE=players&L=11083&W=&JSON=1")
#         players_json = json.loads(page.text)
#         converter = {}
#         for player in players_json['players']['player']:
#             # convert from Doe, John to John Doe
#             name_array = player['name'].split(",")
#             converter[player['id']] = name_array[1] + " " + name_array[0]
#         return converter

#     def __make_id_to_draft_pick_converter__(self):
#         '''
#         current draft picks are formatted as DP_02_05 = 2018 Round 3 Pick 5
#         future draft picks formmated as FP_0005_2018_2
#         where 0005 referes to the franchise id who originally owns the draft pick,
#         then the year and then the round
#         (in this case the rounds are the actual rounds, not one less).
#         '''

#         # (TODO) probably a really cool pythonic way to do this...whatever works for now
#         pick_converter = {}
#         # this year's picks
#         for round_num in range(1, 10):
#             for pick_num in range(1, 20):
#                 # if pick_num < 10:
#                 #     pick_num = '0' + str(pick_num)
#                 # else:
#                 converted_pick = str(
#                     2018) + ' Round ' + str(round_num) + ' Pick ' + str(pick_num)
#                 pick_id = 'DP_' + str(round_num - 1) + '_' + str(pick_num - 1)
#                 pick_converter[pick_id] = converted_pick

#         # future picks
#         for round_num in range(1, 10):
#             for year in range(2018, 2025):
#                 for team_num in range(0, 20):
#                     if team_num < 10:
#                         team_num = '000' + str(team_num)
#                     else:
#                         team_num = '00' + str(team_num)
#                     converted_pick = str(year) + ' Round ' + str(round_num)
#                     pick_id = 'FP_' + str(team_num) + '_' + \
#                         str(year) + '_' + str(round_num)
#                     pick_converter[pick_id] = converted_pick
#         return pick_converter

#     def __get_converter__(self):
#         id_to_players = self.__get_id_to_player_dict__()
#         id_to_draft_pick = self.__make_id_to_draft_pick_converter__()
#         return {**id_to_players, **id_to_draft_pick}


# def __reformat_trade__(trade, league_id):
#     new_trade = trade_dtype()
#     new_trade.league_id = league_id
#     new_trade.fantasy_site = 'mfl'

#     # formatted in strings seperated by commas, turn to list and remove last empty item
#     new_trade.side1 = trade['franchise1_gave_up'].split(',')[:-1]
#     new_trade.side2 = trade['franchise2_gave_up'].split(',')[:-1]
#     new_trade.timestamp = int(trade['timestamp'])
#     new_trade.all_players = new_trade.side1 + new_trade.side2
#     return new_trade


# def __parse_advanced_settings__(settings):
#     ppr = 0

#     for setting in settings['rules']['positionRules']:
#         if isinstance(setting, dict):
#             if 'WR' in setting['positions'].split('|'):
#                 for rule in setting['rule']:
#                     if rule['event']['$t'] == 'CC':
#                         ppr = rule['points']['$t'].split('*')[-1]

#         elif isinstance(setting, str):
#             if 'WR' in settings['rules']['positionRules']['positions'].split('|'):
#                 for rule in settings['rules']['positionRules']['rule']:
#                     if rule['event']['$t'] == 'CC':
#                         ppr = rule['points']['$t'].split('*')[-1]
#             return {
#                 'ppr': ppr
#             }
#     return {
#         'ppr': ppr
#     }


# from bs4 import BeautifulSoup
# import requests
import time


class ESPNService(FantasySiteService):
    name = 'ESPN'
    basic_settings = {'Number of Teams': 'num_teams',
                      'League Name': 'name', 'Quarterback (QB)': 'num_qbs'}

    # dictionary used to rename scoring setting
    advanced_settings = {'Each reception (REC)': 'ppr'}
    league_settings = {}

    def __init__(self, year):
        self.year = year

    def make_trade(self, trade_columns):
        team1 = None
        team2 = None

        # get team name of each trade index
        teams = [team.split(' ')[0]
                 for team in trade_columns[2] if 'traded' in team]

        # make sure only 2 teams (error if team names are the same)
        if len(set(teams)) is not 2:
            raise ValueError

        trade_side1 = []
        trade_side2 = []
        for player, team in zip(trade_columns[2].findAll('b'), teams):
            # if player on espn is injured, they will show as example: Jordy Nelson*
            if player is not None:
                player = player.text.replace('*', '')

            # if first trade item, set team1, add to trade
            if team1 is None and team2 is None:
                team1 = team

                trade_side1.append(player)
            elif team2 is None and team1 == team:
                trade_side1.append(player)
            else:
                team2 = team
                trade_side2.append(player)
        return trade_side1, trade_side2

    def get_trades(self, league_id):
        url = "http://games.espn.com/ffl/recentactivity?leagueId=" + str(league_id) + "&seasonId=" \
              + str(self.year) + \
            "&activityType=2&startDate=20180911&endDate=20181129&teamId=-1&tranType=4"
        try:
            # headers = {
                # 'User-Agent': 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405'}
            page = requests.get(url)
        except Exception as e:
            print(e)
            print(
                'Warning: Unable to download, couldn\'t request trades from:', league_id)
        # return []

        soup = BeautifulSoup(page.text, 'lxml')
        trade_data = []
        tables = soup.findAll('table')

        for transaction in soup.findAll(text="Transaction"):
            trade_table = transaction.parent.parent.parent

            # trades can be accepted and processed, don't want duplicates
            if 'Processed' not in trade_table.text:
                continue

            col = trade_table.find_all('td')
            try:
                trade_side1, trade_side2 = self.make_trade(col)
            except ValueError:
                # print('Warning: Unable to make trade in ESPNServices.get_trades in league', league_id)
                continue

            # Convert date to epoch (example preprocessed format: Wed, Nov 22 7:30 PM)
            date = str(col[0].renderContents()).replace(
                '<br/>', ' ')[2:-4].split(',')[1].lstrip() + " " + str(self.year)
            date_epoch = int(time.mktime(
                time.strptime(date, '%b %d %H:%M %Y')))

            single_trade = trade_dtype()
            single_trade.league_id = league_id
            single_trade.side1 = trade_side1
            single_trade.side2 = trade_side2
            single_trade.timestamp = date_epoch
            single_trade.fantasy_site = self.name
            single_trade.all_players = [*trade_side1, *trade_side2]

            if single_trade is None:
                continue

            single_trade.league_settings = self.get_settings(
                league_id).to_json()

            trade_data.append(single_trade)
        return trade_data

    def get_settings(self, league_id):
        if league_id in self.league_settings:
            return self.league_settings[league_id]

        league_settings = fantasy_league_dtype()

        url = 'http://games.espn.com/ffl/leaguesetup/settings?leagueId=' + \
            str(league_id)
        page = requests.get(url)

        soup = BeautifulSoup(page.text, 'lxml')

        tables = soup.find_all('table', attrs={'class': 'leagueSettingsTable'})

        settings = {}
        league_settings.league_id = league_id
        # PPR scoring defaults to 0, since ESPN does not display this setting if it is 0
        settings['ppr'] = 0

        for table in tables:
            rows = table.find_all('tr')

            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]

                # add to settings dictionary if setting is needed
                if cols[0] in self.basic_settings:
                    settings[self.basic_settings[cols[0]]] = cols[1]

                # check if any advanced settings are in string
                for setting in self.advanced_settings:
                    if setting in cols:
                        settings[self.advanced_settings[setting]
                                 ] = cols[cols.index(setting) + 1]

        settings['league_id'] = league_id
        league_settings.name = settings['name']
        league_settings.num_teams = settings['num_teams']
        league_settings.num_qbs = settings['num_qbs']
        league_settings.ppr = settings['ppr']
        self.league_settings[league_id] = league_settings
        return league_settings

    def get_valid_leagues(self, fast_search=False):
        if fast_search:
            # return leagues which have already been found to have a trade in them
            raise NotImplementedError
        else:
            # return [841145]
            return range(841145, 1726141)


# espn = ESPNService()
# # print(espn.get_settings(842623))
# print(espn.get_trades(841145))
# print(espn.get_settings(841145))


# service = MFLService(2018)
# service.get_settings(35465)
# service.get_settings(10431)
