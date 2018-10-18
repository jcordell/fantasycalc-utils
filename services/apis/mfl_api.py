import requests
import json
import sys
import os.path
libdir = os.path.dirname(__file__)
sys.path.append(os.path.split(libdir)[0])

import time


class mfl_api():
    def get_league_id_page(self):
        page = None
        try:
            page = requests.get(
                "http://www03.myfantasyleague.com/2017/index?YEAR=2017&SEARCH=dynasty&submit=Go")

            # check that page downloaded correctly
            if str(page.status_code)[0] != str(2):
                raise RuntimeError
        except:
            print("Error downloading MFL dynastly league id page.")

        return page.content

    def get_league_trades(self, league_id, year=2018):
        # be nice to the servers
        time.sleep(1)

        trades_json = None
        try:
            trade_url = "http://www55.myfantasyleague.com/" + str(year) + "/export?TYPE=transactions&L=" \
                        + str(league_id) + "&TRANS_TYPE=TRADE&JSON=1"
            trade_page = requests.get(trade_url)
            if trade_page.status_code > 299 or trade_page.status_code < 200:
                raise RuntimeError

            # convert string to json, load trades
            trades_json = json.loads(trade_page.content.decode(
                'utf-8'))['transactions']['transaction']

            # if only one trade from league, still return as list
            if type(trades_json) != list:
                trades_json = [trades_json]

            # convert ids to player names

        except Exception as e:
            print('Error downloading trades for league:',
                  league_id, 'status code:', trade_page.status_code)
            print(e)
        return trades_json

    def get_basic_settings(self, league_id, year=2018):
        settings_url = "http://www.myfantasyleague.com/" + \
            str(year) + "/export?TYPE=league&L=" + \
            str(league_id) + "&APIKEY=&JSON=1"

        try:
            settings_page = requests.get(settings_url)
            if settings_page.status_code > 299 or settings_page.status_code < 200:
                raise RuntimeError

            return json.loads(settings_page.content.decode('utf-8'))
        except Exception as e:
            print('unable to get settings for', league_id)
            print(e)

    def get_advanced_settings(self, league_id, year=2018):
        settings_url = 'http://www.myfantasyleague.com/' + \
            str(year) + '/export?TYPE=rules&L=' + str(league_id) + '&JSON=1'
        try:
            settings_page = requests.get(settings_url)
            if settings_page.status_code > 299 or settings_page.status_code < 200:
                raise RuntimeError
            return json.loads(settings_page.content.decode('utf-8'))

        except Exception as e:
            print('unable to get settings for', league_id)
            print(e)

    def get_valid_leagues(self, fast_search=True):
        pass
