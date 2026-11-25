import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from dateutil.relativedelta import relativedelta
from sense_hat import SenseHat  # ty: ignore[unresolved-import]  # Pi-only dep


def main(team_id):
    sense = SenseHat()

    local_tz = ZoneInfo("America/Los_Angeles")
    now = datetime.now(local_tz)

    url = f"http://statsapi.mlb.com/api/v1/schedule/games?teamId={team_id}&sportId=1"
    r = requests.get(url)

    total_games = r.json().get("totalGames")

    for i in range(total_games):
        game_time = r.json().get("dates")[i].get("games")[0].get("gameDate")
        away_team = (
            r.json()
            .get("dates")[i]
            .get("games")[0]
            .get("teams")
            .get("away")
            .get("team")
            .get("name")
        )
        home_team = (
            r.json()
            .get("dates")[i]
            .get("games")[0]
            .get("teams")
            .get("home")
            .get("team")
            .get("name")
        )
        home_team_id = (
            r.json()
            .get("dates")[i]
            .get("games")[0]
            .get("teams")
            .get("home")
            .get("team")
            .get("id")
        )
        game_time = datetime.fromisoformat(game_time).astimezone(local_tz)
        minute_diff = relativedelta(now, game_time).minutes
        hour_diff = relativedelta(now, game_time).hours
        day_diff = relativedelta(now, game_time).days
        month_diff = relativedelta(now, game_time).months
        game_time_hour = str(game_time.hour)
        game_time_minute = "0" + str(game_time.minute)
        game_time = game_time_hour + ":" + game_time_minute[-2:]

        away_wins = (
            r.json()
            .get("dates")[i]
            .get("games")[0]
            .get("teams")
            .get("away")
            .get("leagueRecord")
            .get("wins")
        )
        away_loss = (
            r.json()
            .get("dates")[i]
            .get("games")[0]
            .get("teams")
            .get("away")
            .get("leagueRecord")
            .get("losses")
        )
        away_record = f"{away_wins}-{away_loss}"
        home_wins = (
            r.json()
            .get("dates")[i]
            .get("games")[0]
            .get("teams")
            .get("home")
            .get("leagueRecord")
            .get("wins")
        )
        home_loss = (
            r.json()
            .get("dates")[i]
            .get("games")[0]
            .get("teams")
            .get("home")
            .get("leagueRecord")
            .get("losses")
        )
        home_record = f"{home_wins}-{home_loss}"

        if (
            month_diff == 0
            and day_diff == 0
            and hour_diff == 0
            and 0 >= minute_diff >= -10
        ):
            if home_team_id == team_id:
                msg = f"The {home_team} ({home_record}) will be playing the {away_team} ({away_record}) at {game_time}"
            else:
                msg = f"The {home_team} ({home_record}) will be playing at the {away_team} ({away_record}) at {game_time}"
            sense.show_message(msg, scroll_speed=0.05)

        if (
            month_diff == 0
            and day_diff == 0
            and hour_diff == 0
            and (minute_diff == -1 or minute_diff == -5)
        ):
            subprocess.run(
                [
                    "mpv",
                    "--fs",
                    "/home/ryan/Documents/rpi-dodgers/dodger_baseball.mp3",
                ],
                check=False,
            )
    try:
        game_ID = r.json().get("dates")[0].get("games")[0].get("gamePk")
        run_checker(game_ID, team_id)
    except (AttributeError, IndexError):
        pass


def run_checker(game_id, team_id):
    # The live feed is only served at v1.1; v1 returns 404.
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_id}/feed/live"
    feed = requests.get(url).json()

    now = datetime.now(ZoneInfo("America/Los_Angeles"))
    sense = SenseHat()

    teams = feed["gameData"]["teams"]
    plays = feed["liveData"]["plays"]
    for i in plays["scoringPlays"]:
        play = plays["allPlays"][i]
        # Plays don't name the scoring team; the away team bats in the top half.
        batting = "away" if play["about"]["halfInning"] == "top" else "home"
        if teams[batting]["id"] != team_id:
            continue
        scored_at = datetime.fromisoformat(play["about"]["endTime"])
        if 0 <= (now - scored_at).total_seconds() < 3 * 60:
            result = play["result"]
            score = f"{result['awayScore']}-{result['homeScore']}"
            run_msg = (
                f"run!!!! {result['description'].rstrip('.')}. The score is {score}"
            )
            sense.show_message(run_msg, scroll_speed=0.05)


if __name__ == "__main__":
    main(
        119
    )  # This is the code for the Dodgers; the ID can be found here: http://statsapi.mlb.com/api/v1/teams?sportId=1
