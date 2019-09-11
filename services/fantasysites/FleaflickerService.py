# from services.apis.fleaflicker_api import fleaflicker_api

import requests
import json
from bs4 import BeautifulSoup
import re
import collections
from datetime import date
from dateutil.relativedelta import relativedelta
import time
import json
import codecs
import unicodedata


class fleaflicker_api():
    base_url = "https://www.fleaflicker.com/nfl/leagues"

    def get_trades(self, league_id, offset=0):
        response = requests.get(self.base_url + "/" + str(league_id) +
                                '/transactions?transactionType=TRADE&tableOffset=' + str(offset))
        response.raise_for_status()
        return response.content

    def get_rules(self, league_id):
        response = requests.get(self.base_url + "/" +
                                str(league_id) + "/rules")
        response.raise_for_status()
        return response.content

    def get_teams(self, league_id):
        response = requests.get(self.base_url + '/' +
                                str(league_id) + '/teams')
        response.raise_for_status()
        return response.content

    def get_scoring(self, league_id):
        response = requests.get(self.base_url + "/" +
                                str(league_id) + "/scoring")
        response.raise_for_status()
        return response.content


class FleaflickerConverter():
    trade_teamname_converter = {}

    def toTrades(self, raw_html, trades={}):
        soup = BeautifulSoup(raw_html, "html.parser")
        player_divs = soup.find_all('div', {'class': 'list-group-item-text'})
        for div in player_divs:
            # try to parse player
            trade_string = self.remove_special_chars(div.text)
            traded, team1, team2 = self.parse_trade_string(trade_string)

            # get trade id
            trade_url = div.find_all('a', href=True)
            trade_id = trade_url[1]['href'].split("/")[-1]
            trades, finished = self.add_to_trade(
                trades, trade_id, traded, str(team1), str(team2), trade_string)
            if finished:
                return trades, 0
        return trades, len(player_divs)

    def remove_special_chars(self, s):
        return unicodedata.normalize('NFKD', s)

    def add_to_trade(self, trades, trade_id, traded, team1, team2, trade_string):
        if trade_id not in trades:
            trades[trade_id] = {}
            self.trade_teamname_converter[trade_id] = {}
            self.trade_teamname_converter[trade_id][team2] = 'side1'
            trades[trade_id]['side1'] = []
        if team2 not in self.trade_teamname_converter[trade_id]:
            self.trade_teamname_converter[trade_id][team2] = 'side2'
            trades[trade_id]['side2'] = []

        if 'date' not in trades[trade_id]:
            trades[trade_id]['date'] = self.parse_relative_date(
                trade_string)
            if trades[trade_id]['date'] is None:
                del(trades[trade_id])
                return trades, True

        trades[trade_id][self.trade_teamname_converter[trade_id]
                         [team2]].append(traded)
        return trades, False

    def parse_trade_string(self, s):
        # Cat People traded for Jordan Thomas from Mr Beez Ballz 3 weeks ago
        team1 = s.split(' traded for')[0]
        # not actually parsing team names, just using to format trades
        team2 = s.split('from ')[-1]
        player = self.find_between(s, ' traded for ', ' from')
        return player, team1, team2

    def parse_relative_date(self, trade_string):
        trade_string = trade_string.split(' ')

        if 'hour' in trade_string or 'hours' in trade_string:
            date_time = date.today() - relativedelta(hours=+
                                                     int(trade_string[-3]))
        elif 'day' in trade_string or 'days' in trade_string:
            date_time = date.today() - relativedelta(days=+
                                                     int(trade_string[-3]))
        elif 'week' in trade_string or 'weeks' in trade_string:
            date_time = date.today() - relativedelta(weeks=+
                                                     int(trade_string[-3]))
        elif 'month' in trade_string or 'months' in trade_string:
            date_time = date.today() - relativedelta(months=+
                                                     int(trade_string[-3]))
        elif 'year' in trade_string or 'years' in trade_string:
            # date_time = date.today() - relativedelta(years=+
            #                                          int(trade_string[-3]))
            # don't parse anything older than a year
            return None

        pattern = '%Y-%M-%d'
        epoch = int(time.mktime(time.strptime(str(date_time), pattern)))
        return epoch

    def find_between(self, s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    def parse_rules(self, raw_html):
        def parse_league_type(text):
            if 'Keepers' in text:
                return True
            else:
                return False
        soup = BeautifulSoup(raw_html, "html.parser")
        name = soup.find('meta', property="og:title")['content']
        dynasty = parse_league_type(soup.text)

        rules = soup.find_all('span', {'class': 'position tt-content'})
        num_qbs = int(rules[0].find_previous_sibling('strong').text)
        num_superflex = int(rules[3].find_previous_sibling('strong').text)
        num_qbs += num_superflex
        return name, dynasty, num_qbs

    def parse_num_teams(self, raw_html):
        soup = BeautifulSoup(raw_html, "html.parser")
        return len(soup.find_all('span', {'class': 'league-name'}))

    def parse_ppr(self, raw_html):
        soup = BeautifulSoup(raw_html, "html.parser")
        # soup.find('h3', string='Receiving')
        scoring = soup.find_all('td')
        ppr = 0
        for score in scoring:
            if 'for every Catch' in score.text:
                ppr = score.text.split(' ')[0]
        return ppr


class FleaflickerService():
    client = fleaflicker_api()
    converter = FleaflickerConverter()

    def get_trades(self, league_id):
        raw_response = self.client.get_trades(league_id)
        trades, offset = self.converter.toTrades(raw_response)
        while True:
            raw_response = self.client.get_trades(league_id, offset)
            trades, paged_items = self.converter.toTrades(raw_response, trades)
            offset += paged_items

            if paged_items == 0:
                break
        return trades

    def get_settings(self, league_id):
        raw_response = self.client.get_rules(league_id)
        name, is_dynasty, num_qbs = self.converter.parse_rules(raw_response)

        raw_response = self.client.get_teams(league_id)
        num_teams = self.converter.parse_num_teams(raw_response)

        raw_response = self.client.get_scoring(league_id)
        ppr = self.converter.parse_ppr(raw_response)
        print(name, is_dynasty, num_qbs, num_teams, ppr)


service = FleaflickerService()
service.get_settings(138415)

redraft_league_id = 58521
# service.get_settings(redraft_league_id)
