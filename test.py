import requests
from sense_hat import SenseHat
from datetime import datetime
import pytz
from dateutil.relativedelta import relativedelta
import os



def main(team_id):
	pass

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
