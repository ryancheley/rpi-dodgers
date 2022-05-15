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

        away_wins = (r.json().get('dates')[i].get('games')[0].get('teams').get('away').get('leagueRecord').get('wins'))
        away_loss = (r.json().get('dates')[i].get('games')[0].get('teams').get('away').get('leagueRecord').get('losses'))
        away_record = '{}-{}'.format(away_wins, away_loss)
        home_wins = (r.json().get('dates')[i].get('games')[0].get('teams').get('home').get('leagueRecord').get('wins'))
        home_loss = (r.json().get('dates')[i].get('games')[0].get('teams').get('home').get('leagueRecord').get('losses'))
        home_record = '{}-{}'.format(home_wins, home_loss)

        if month_diff == 0 and day_diff == 0 and hour_diff == 0 and 0 >= minute_diff >= -10:
            if home_team_id == team_id:
                msg = 'The {} ({}) will be playing the {} ({}) at {}'.format(home_team, home_record, away_team, away_record ,game_time)
            else:
                msg = 'The {} ({}) will be playing at the {} ({}) at {}'.format(home_team, home_record, away_team, away_record ,game_time)
            sense.show_message(msg, scroll_speed=0.05)

        if month_diff == 0 and day_diff == 0 and hour_diff == 0 and (minute_diff == -1 or minute_diff == -5):      
            os.system("omxplayer -b /home/pi/Documents/python_projects/itfdb/dodger_baseball.mp3")
    game_ID = r.json().get('dates')[0].get('games')[0].get('gamePk')
    run_checker(game_ID, team_id)
    

def run_checker(game_id, team_id):
    url = 'http://statsapi.mlb.com/api/v1/game/{}/feed/live'.format(game_id)
    r = requests.get(url)

    local_tz = pytz.timezone('America/Los_Angeles')
    utc_now = pytz.utc.localize(datetime.utcnow())
    now = utc_now.astimezone(local_tz)
    sense = SenseHat()


    scoring_plays = r.json().get('liveData').get('plays').get('scoringPlays')

    for i in range(len(scoring_plays)):
        run_team_id = r.json().get('liveData').get('plays').get('allPlays')[scoring_plays[i]].get('team').get('id')
        run_ts = r.json().get('liveData').get('plays').get('allPlays')[scoring_plays[i]].get('about').get('dateTime')
        run_ts = datetime.strptime(run_ts, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc).astimezone(local_tz)
        minute_diff = relativedelta(now, run_ts).minutes
        hour_diff = relativedelta(now, run_ts).hours
        day_diff = relativedelta(now, run_ts).days
        month_diff = relativedelta(now, run_ts).months
        run_ts_hour = str(run_ts.hour)
        run_ts_minute = '0'+str(run_ts.minute)
        run_ts = run_ts_hour+":"+run_ts_minute[-2:]
        if month_diff == 0 and day_diff == 0 and hour_diff == 0 and 2 >= minute_diff >= 0:
            if run_team_id == team_id:
                score_away = r.json().get('liveData').get('boxscore').get('teams').get('away').get('teamStats').get('teamSkaterStats').get('runs')
                score_home = r.json().get('liveData').get('boxscore').get('teams').get('home').get('teamStats').get('teamSkaterStats').get('runs')
                score = '{}-{}'.format(score_away, score_home)
                run_msg = 'run!!!! '+r.json().get('liveData').get('plays').get('allPlays')[scoring_plays[i]].get('result').get('description')+'. The score is {}'.format(score)
                sense.show_message(run_msg, scroll_speed=0.05)



if __name__ == '__main__':
    main(119) # This is the code for the Dodgers; the ID can be found here: http://statsapi.mlb.com/api/v1/teams?sportId=1
