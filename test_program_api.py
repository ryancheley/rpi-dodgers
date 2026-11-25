"""Offline checks for run_checker. Run with `uv run python test_program_api.py`."""

import sys
from datetime import datetime, timedelta
from unittest import mock

sense = mock.MagicMock()
sys.modules["sense_hat"] = mock.MagicMock(SenseHat=lambda: sense)

import program_api

DODGERS = 119


def play(half, end, away, home, desc):
    return {
        "about": {"halfInning": half, "endTime": end},
        "result": {"awayScore": away, "homeScore": home, "description": desc},
    }


# Trimmed from the real v1.1 feed for game 849810 (Brewers @ Dodgers, 2026-10-15).
FEED = {
    "gameData": {"teams": {"away": {"id": 158}, "home": {"id": DODGERS}}},
    "liveData": {
        "plays": {
            "scoringPlays": [0, 1],
            "allPlays": [
                play("bottom", "2026-10-16T00:45:02.082Z", 0, 1, "Andy Pages singles."),
                play("top", "2026-10-16T01:13:47.966Z", 2, 4, "Brewers homer."),
            ],
        }
    },
}


def shows_at(now: datetime) -> list[str]:
    fixed = mock.MagicMock(wraps=datetime)
    fixed.now.return_value = now
    sense.reset_mock()
    with (
        mock.patch.object(program_api, "datetime", fixed),
        mock.patch.object(program_api, "requests") as requests,
    ):
        requests.get.return_value.json.return_value = FEED
        program_api.run_checker(849810, DODGERS)
    return [c.args[0] for c in sense.show_message.call_args_list]


dodger_run = datetime.fromisoformat("2026-10-16T00:45:02.082Z")
assert shows_at(dodger_run + timedelta(minutes=1)) == [
    "run!!!! Andy Pages singles. The score is 0-1"
]
assert shows_at(dodger_run - timedelta(seconds=1)) == []  # not yet scored
assert shows_at(dodger_run + timedelta(minutes=4)) == []  # too long ago
brewers_run = datetime.fromisoformat("2026-10-16T01:13:47.966Z")
assert shows_at(brewers_run + timedelta(minutes=1)) == []  # other team's run
print("ok")
