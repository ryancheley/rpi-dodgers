

class Schedule:
    def __init__(self, game_date, game_opponent, game_time, game_date_time):
        self.game_date = game_date
        self.game_opponent = game_opponent
        self.game_time = game_time
        self.game_date_time = game_date_time

    @staticmethod
    def create_from_dict(lookup):
        return Schedule(
            lookup['game_date'],
            lookup['game_opponent'],
            lookup['game_time'],
            lookup['game_date_time']
        )
