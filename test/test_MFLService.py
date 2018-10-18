# append project to system path to make modules findable
import sys
sys.path.append('/home/josh/Documents/FantasyFootballCalculator')

from services.fantasysites.MFLService import MFLService
import requests
from config import TestConfig as config

class Content:
    def __init__(self, content):
        self.content = content

    def decode(self, args):
        return self.content


class MockLeagueListResponse:
    def __init__(self, content, status_code):
        self.content = content
        self.status_code = status_code
        self.decode = content

class MockTradeResponse:
    def __init__(self, content, status_code):
        self.content = Content(content)
        self.status_code = status_code
        self.decode = content


def get_mock_league_list_response():
    with open('/home/josh/Documents/FantasyFootballCalculator'
              '/test/test_data/dynastyleaguepage.txt', 'r') as dynastypage:

        return MockLeagueListResponse(dynastypage.read(), 200)


def get_mock_trade_response():
    with open('/home/josh/Documents/FantasyFootballCalculator'
              '/test/test_data/mfl_trades.txt', 'r') as tradepage:
        return MockTradeResponse(tradepage.read(), 200)


def test_get_valid_leagues(mocker):
    # mock request.get response for getting the dynasty league search page form mfl
    mocker.patch.object(requests, 'get')
    requests.get.return_value = get_mock_league_list_response()

    mfl = MFLService(config)
    leagues = mfl.get_valid_leagues()

    # 4509 leagues in the mock response
    assert len(leagues) == 4509


def test_get_league_trades(mocker):
    # mock request.get for mfl transactions api endpoint
    mocker.patch.object(requests, 'get')
    requests.get.return_value = get_mock_trade_response()

    mfl = MFLService(config)
    league_trades = mfl.get_trades(57183)

    assert league_trades[0].side1 == ['9884', 'FP_0012_2018_1']
    assert league_trades[0].timestamp == 1510711238
