import requests
from sense_hat import SenseHat
from datetime import datetime
import pytz
from dateutil.relativedelta import relativedelta
import os



def main(team_id):
    sense = SenseHat()

    local_tz = pytz.timezone('America/Los_Angeles')
    utc_now = pytz.utc.localize(datetime.utcnow())
    now = utc_now.astimezone(local_tz)

    url = 'http://statsapi.mlb.com/api/v1/schedule/games?teamId={}&sportId=1'.format(team_id)
    r = requests.get(url)

    total_games = r.json().get('totalGames')

    for i in range(total_games):
        game_time = (r.json().get('dates')[i].get('games')[0].get('gameDate'))
        away_team = (r.json().get('dates')[i].get('games')[0].get('teams').get('away').get('team').get('name'))
        home_team = (r.json().get('dates')[i].get('games')[0].get('teams').get('home').get('team').get('name'))
        away_team_id = (r.json().get('dates')[i].get('games')[0].get('teams').get('away').get('team').get('id'))
        home_team_id = (r.json().get('dates')[i].get('games')[0].get('teams').get('home').get('team').get('id'))
        game_time = datetime.strptime(game_time, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc).astimezone(local_tz)
        minute_diff = relativedelta(now, game_time).minutes
        hour_diff = relativedelta(now, game_time).hours
        day_diff = relativedelta(now, game_time).days
        month_diff = relativedelta(now, game_time).months
        game_time_hour = str(game_time.hour)
        game_time_minute = '0'+str(game_time.minute)
        game_time = game_time_hour+":"+game_time_minute[-2:]
        away_record = return_record(away_team_id)
        home_record = return_record(home_team_id)        
        if month_diff == 0 and day_diff == 0 and hour_diff == 0 and 0 >= minute_diff >= -10:
            if home_team_id == team_id:
                msg = 'The {} ({}) will be playing the {} ({}) at {}'.format(home_team, home_record, away_team, away_record ,game_time)
            else:
                msg = 'The {} ({}) will be playing at the {} ({}) at {}'.format(home_team, home_record, away_team, away_record ,game_time)
            sense.show_message(msg, scroll_speed=0.05)

        if month_diff == 0 and day_diff == 0 and hour_diff == 0 and (minute_diff == -1 or minute_diff == -5):      
            os.system("omxplayer -b /home/pi/Documents/python_projects/itfdb/dodger_baseball.mp3")


def return_record(team_id):
    standings_url = 'https://statsapi.web.nhl.com/api/v1/teams/{}/stats'.format(team_id)
    r = requests.get(standings_url)
    wins = (r.json().get('stats')[0].get('splits')[0].get('stat').get('wins'))
    losses = (r.json().get('stats')[0].get('splits')[0].get('stat').get('losses'))
    otl = (r.json().get('stats')[0].get('splits')[0].get('stat').get('ot'))
    record = str(wins)+'-'+str(losses)+'-'+str(otl)
    return record


if __name__ == '__main__':
    main(119) # This is the code for the Dodgers; the ID can be found here: http://statsapi.mlb.com/api/v1/teams?sportId=1
