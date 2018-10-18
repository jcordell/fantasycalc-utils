import csv
import sys
import re
sys.path.append('/Users/jkc023/Documents/homecode/fantasycalc-utils')
from services.MongoDB import MongoDB
import numpy as np


def load_csv_ranking(path):
    # print(path)
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        rankings = []
        for row in csv_reader:
            # remove special chars from player names
            for name in range(2, len(row)):
                row[name] = re.sub(r"[^a-zA-Z0-9]+", ' ', row[name]).strip()

            rankings.append(row)
        return rankings


def make_player_rankings(table):
    player_rankings = {}
    for row in table:
        # 0 index is tier, 1 index is value, rest are player names
        for player_index in range(2, len(row)):
            if len(row[player_index]) != 0:
                player_value = {}
                player_value['value'] = row[1]
                player_value['tier'] = row[0]
                player_rankings[row[player_index]] = player_value
    # print(player_rankings)
    return player_rankings


def load_week(week):
    base_path = '../../data/playervalue/week' + str(week) + '/'

    league_types = ['standard', 'halfppr', 'ppr']

    week_rankings = {}
    for setting in league_types:
        rankings = load_csv_ranking(base_path + setting + '.csv')
        values = make_player_rankings(rankings)
        week_rankings[setting] = {
            'rankings': rankings,
            'values': values
        }

    return week_rankings


# if player has increased or decreased in value over both of the last weeks, return that value
# if player went up and down return 0
def get_trend(weekly_values):
    if len(weekly_values) < 3:
        return 0
    elif weekly_values[0] < weekly_values[1] and weekly_values[1] < weekly_values[2]:
        return weekly_values[2] - weekly_values[0]
    elif weekly_values[0] > weekly_values[1] and weekly_values[1] > weekly_values[2]:
        return weekly_values[2] - weekly_values[0]
    else:
        return 0


def add_trend_to_row(season_rankings, row, week, league_type):
    for i in range(2, len(row)):
        if row[i] == '':
            continue
        row[i] = {
            'name': row[i],
            'trend': float(season_rankings[week][league_type]['values'][row[i]]['trend'])
        }
    return row


def calculate_player_trends(season_rankings, startweek, endweek):
    league_types = ['standard', 'halfppr', 'ppr']

    for league_type in league_types:
        for player in season_rankings['Week ' + str(endweek)][league_type]['values']:
            # get the values of the player from the startweek to now in an array
            player_weekly_values = []
            for num_week in range(startweek, endweek + 1):

                week_value = 0
                if player in season_rankings['Week ' +
                                             str(num_week)][league_type]['values']:

                    week_value = season_rankings['Week ' +
                                                 str(num_week)][league_type]['values'][player]['value']
                player_weekly_values.append(float(week_value))
            # add trend to player object
            season_rankings['Week ' +
                            str(num_week)][league_type]['values'][player]['trend'] = get_trend(player_weekly_values)
            # add name to player object for easier parsing on frontend
            season_rankings['Week ' +
                            str(num_week)][league_type]['values'][player]['name'] = player

        # need to add trend to every table row so UI renders faster
        for index in range(len(season_rankings['Week ' + str(endweek)][league_type]['rankings'])):
            row = season_rankings['Week ' +
                                  str(endweek)][league_type]['rankings'][index]
            row = add_trend_to_row(season_rankings, row,
                                   'Week ' + str(endweek), league_type)
            season_rankings['Week ' +
                            str(endweek)][league_type]['rankings'][index] = row
            print(row)

    return season_rankings


def load_season(num_weeks):
    season_rankings = {}
    for week in range(1, num_weeks + 1):
        season_rankings['Week ' + str(week)] = load_week(week)
        start_week = week - 2

        if start_week < 1:
            start_week = 1
        season_rankings = calculate_player_trends(
            season_rankings, start_week, week)
    return season_rankings


season_rankings = load_season(7)
print('created rankings')
# connect to db and insert rankings
db = MongoDB()
db.connect('localhost')
print('connected to db')
db.insert_rankings(season_rankings)
print('finished inserting rankings')

# print(week_rankings)
