from sense_hat import SenseHat  # ty: ignore[unresolved-import]  # Pi-only dep
import subprocess


def main():
    sense = SenseHat()
    message = "#ITFDB!!! The Dodgers will be playing San Francisco at 5:37pm tonight!"
    sense.show_message(message, scroll_speed=0.05)
    subprocess.run(
        [
            "omxplayer",
            "-b",
            "/home/pi/Documents/python_projects/itfdb/dodger_baseball.mp3",
        ]
    )


if __name__ == "__main__":
    main()
