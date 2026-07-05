# rpi-dodgers

A Raspberry Pi + [Sense HAT](https://www.raspberrypi.com/products/sense-hat/)
ticker that scrolls upcoming MLB game info across the LED matrix and announces
scoring plays. It polls the public MLB Stats API and, by default, tracks the
Los Angeles Dodgers (team ID `119`).

- `program_api.py` — the main program: fetches the schedule, scrolls the next
  game on the Sense HAT, plays a walk-up sound at game time, and announces runs.
- `demo.py` — a minimal standalone demo that just scrolls a message and plays a
  sound. Useful for confirming your Sense HAT and audio work.

## Hardware

- Raspberry Pi (any model with the 40-pin GPIO header)
- Sense HAT seated on the GPIO header
- Speakers/headphones (or HDMI audio) for the walk-up sound

## Raspberry Pi setup

Run these on the Pi (Raspberry Pi OS).

### 1. System packages

The Sense HAT Python library depends on `python3-rtimulib`, which is **not**
available from PyPI — it must come from `apt`. `mpv` plays the audio clip.

```bash
sudo apt update
sudo apt install -y sense-hat python3-rtimulib mpv
```

`sense-hat` (apt) pulls in the Sense HAT Python module plus `python3-rtimulib`
and the required kernel/I2C bits.

### 2. Enable I2C

The Sense HAT talks to the Pi over I2C:

```bash
sudo raspi-config    # Interface Options -> I2C -> Enable
sudo reboot
```

### 3. Get the code

```bash
git clone https://github.com/ryancheley/rpi-dodgers.git
cd rpi-dodgers
```

### 4. Install the Python dependencies

Because the Sense HAT library is installed system-wide via `apt` (it can't come
from PyPI), the simplest path on the Pi is to install the remaining pure-Python
deps with `apt` too and run against the system Python:

```bash
sudo apt install -y python3-requests python3-dateutil
```

<details>
<summary>Alternative: use a virtual environment</summary>

If you prefer a venv, create it with access to the apt-installed `sense_hat`
module (which lives in the system site-packages):

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install requests python-dateutil
```

`sense-hat` is declared in `pyproject.toml` as a Linux-only dependency, but on
the Pi it comes from `apt` (for `rtimulib`), which is why `--system-site-packages`
is needed rather than a plain `pip install`.
</details>

### 5. Configure

Two things are currently hard-coded and may need editing:

- **Team**: `program_api.py` ends with `main(119)` (Dodgers). Change `119` to
  your team's ID — find it at
  <http://statsapi.mlb.com/api/v1/teams?sportId=1>.
- **Audio path**: `program_api.py` runs
  `mpv --fs /home/ryan/Documents/rpi-dodgers/dodger_baseball.mp3`. Update that
  path to wherever you cloned the repo (the `dodger_baseball.mp3` file ships
  with it).

### 6. Run

```bash
python3 demo.py          # quick hardware/audio check
python3 program_api.py   # the real thing
```

The program checks the schedule once per run. To have it run automatically,
schedule it with `cron` — for example, every 5 minutes during the season:

```cron
*/5 * * * * cd /home/ryan/Documents/rpi-dodgers && /usr/bin/python3 program_api.py
```

## Updating the code on the Pi

The Pi pulls its own updates from GitHub — there is no push-based deploy.
Add a `cron` job that `git pull`s the latest `main`, e.g. every 5 minutes:

```cron
*/5 * * * * cd /home/ryan/Documents/rpi-dodgers && /usr/bin/git pull --ff-only >> /home/ryan/rpi-dodgers-pull.log 2>&1
```

So merges to `main` land on the Pi automatically within a few minutes. Edit
`crontab -e` on the Pi to add it.

## Development (non-Pi)

The project uses [uv](https://docs.astral.sh/uv/). On a non-Pi machine the
Sense HAT dependency is skipped automatically (it's marked Linux-only), so you
can still lint and type-check:

```bash
uv sync
uv run ruff check .
uv run ty check
pre-commit install    # run the hooks on every commit
```
