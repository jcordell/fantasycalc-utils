import sys
from services.MongoDB import MongoDB
import time
import json
import requests
import re
from bs4 import BeautifulSoup
from datatypes.fantasy_league import fantasy_league_dtype
from datatypes.trade import trade_dtype
from services.apis.mfl_api import mfl_api
from services.fantasysites.FantasySiteService import FantasySiteService
from ff_espn_api import League
sys.path.append('/Users/jcordell/code/fantasycalc-utils/')


class NumStartersIndex:
    qb = '0'
    super_flex = None  # TODO: get superflex position (OP)


class ESPNService(FantasySiteService):
    name = 'ESPN'
    basic_settings = {'Number of Teams': 'num_teams',
                      'League Name': 'name', 'Quarterback (QB)': 'num_qbs'}

    # dictionary used to rename scoring setting
    advanced_settings = {'Each reception (REC)': 'ppr'}
    league_settings = {}

    def __init__(self, year):
        self.year = year
        # self._db = MongoDB()
        # self._db.connect()

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

        url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/2019/segments/0/leagues/" + str(league_id) + \
            "?rosterForTeamId=1&scoringPeriodId=1&view=mDraftDetail&view=mLiveScoring&view=mMatchupScore&view=mPendingTransactions&view=mPositionalRatings&view=mRoster&view=mSettings&view=mTeam&view=modular&view=mNav"
        try:
            response = requests.get(url)
            response.raise_for_status()
            raw_settings = json.loads(response.text)
            return self.parse_settings(raw_settings, league_id)
        except:
            return None

    def parse_scoring_setting(self, settings_list, scoring_setting_id):
        for setting in settings_list:
            if setting['statId'] == scoring_setting_id:
                if setting['points'] is not None:
                    return setting['points']
                else:
                    return 0

    def parse_settings(self, league, league_id):
        espn_setting_ids = {
            'ppr': 53
        }
        settings = league['settings']
        scoring_settings = settings['scoringSettings']['scoringItems']
        ppr = self.parse_scoring_setting(
            scoring_settings, espn_setting_ids['ppr'])
        num_teams = settings['size']
        name = settings['name']
        roster_settings = settings['rosterSettings']
        num_qbs = roster_settings['lineupSlotCounts'][NumStartersIndex.qb]
        return fantasy_league_dtype({
            'name': name,
            'num_teams': num_teams,
            'league_id': league_id,
            'ppr': ppr,
            'num_qbs': num_qbs,
            'site': 'ESPN'
        })

    def get_valid_leagues(self, fast_search=False):
        if fast_search:
            # return leagues which have already been found to have a trade in them
            raise NotImplementedError
        else:
            # return [841145]
            return range(841145 + 108634, 1726141)
            # return range(930430, 1726141)
            # updated this after college lib
            # return range(1264529 + 35533 + 16262 + 8772, 1726141)
            # league_ids = self._db.get_league_ids('ESPN')
            # print(league_ids)
            # print(len(league_ids))
            # return league_ids


# espn = ESPNService()
# print(espn.get_settings(842623))
# print(espn.get_trades(841145))
# print(espn.get_settings(841145))
# league = League(841145, 2019)
# print(league)
