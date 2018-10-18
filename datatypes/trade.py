class trade_dtype:
    def __init__(self):
        self.league_id = None
        self.fantasy_site = None
        self.side1 = []
        self.side2 = []
        self.all_players = []
        self.timestamp = None
        # could duplicate fantasy league object here
        self.league_settings = None

    def to_json(self):
        return self.__dict__
