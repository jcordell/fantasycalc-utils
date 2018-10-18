'''
settings stored for a fantasy league
'''


class fantasy_league_dtype:
    def __init__(self):
        self.name = None
        self.league_id = None
        self.site = None
        self.num_teams = None
        self.num_qbs = None
        self.ppr = None

    def to_json(self):
        return self.__dict__
