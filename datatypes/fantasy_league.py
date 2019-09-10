'''
settings stored for a fantasy league
'''


class fantasy_league_dtype:
    def __init__(self, league=None):
        if league is not None:
            self.name = league['name']
            self.league_id = league['league_id']
            self.site = league['site']
            self.num_teams = league['num_teams']
            self.num_qbs = league['num_qbs']
            self.ppr = league['ppr']
            self.keepers = league['keepers']
        else:
            self.name = None
            self.league_id = None
            self.site = None
            self.num_teams = None
            self.num_qbs = None
            self.ppr = None
            self.keepers = None

    def to_json(self):
        return self.__dict__
