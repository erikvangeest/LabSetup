import argparse
import os
import sys
import time
from datetime import datetime

import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1523608628169412649/7FoqvXRVKYGcSBow4kFFg3QiQs8AnDZphdeb-p5w4iUbujg6VUup4ZXY5Se58G6NOCnZ"
CHECK_INTERVAL = 5
DISCREPANCY_RATIO = 0.20
ALERT_WINDOW = 600
HEARTBEAT_HOUR = 10
HEARTBEAT_MINUTE = 0


def send_alert(setpoint: float, actual: float, duration_min: float):
    pct = abs(actual - setpoint) / abs(setpoint) * 100
    payload = {
        "content": (
            f"@everyone **MFC Alert**\n"
            f"• Setpoint: `{setpoint}`\n"
            f"• Actual: `{actual}`\n"
            f"• Discrepancy: `{pct:.1f}%`\n"
            f"• Duration: `{duration_min:.1f} min`"
        )
    }
    resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
    resp.raise_for_status()


def send_heartbeat():
    now = datetime.now()
    payload = {
        "content": (
            f"**MFC Heartbeat**\n"
            f"• Status: Monitoring active\n"
            f"• Time: {now:%Y-%m-%d %H:%M:%S}"
        )
    }
    resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
    resp.raise_for_status()
    print(f"[{now:%H:%M:%S}] Heartbeat sent")


def monitor(setpoint: float, actual: float):
    on_time = 0.0
    alerted = False
    last_heartbeat_date = None

    print(
        f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Monitoring setpoint={setpoint}, actual={actual}"
    )
    print(f"  Threshold: {DISCREPANCY_RATIO*100:.0f}% for {ALERT_WINDOW//60} min")

    while True:
        time.sleep(CHECK_INTERVAL)

        now = datetime.now()
        if (
            last_heartbeat_date != now.date()
            and now.hour == HEARTBEAT_HOUR
            and now.minute == HEARTBEAT_MINUTE
        ):
            send_heartbeat()
            last_heartbeat_date = now.date()

        setpoint = abs(setpoint)
        discrepancy = (
            abs(actual - setpoint) / setpoint if setpoint != 0 else float("inf")
        )

        if discrepancy > DISCREPANCY_RATIO:
            on_time += CHECK_INTERVAL
            if on_time % 60 < CHECK_INTERVAL:
                print(
                    f"[{now:%H:%M:%S}] Discrepancy {discrepancy*100:.1f}% for {on_time/60:.1f} min"
                )
            if on_time >= ALERT_WINDOW and not alerted:
                send_alert(setpoint, actual, on_time / 60)
                alerted = True
                print(f"[{now:%H:%M:%S}] ALERT SENT @everyone")
        else:
            if on_time > 0:
                print(
                    f"[{now:%H:%M:%S}] Normal ({discrepancy*100:.1f}%), was elevated {on_time/60:.1f} min"
                )
            on_time = 0.0
            alerted = False


def parse_stdin():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            try:
                yield float(parts[0]), float(parts[1])
            except ValueError:
                continue


def main():
    parser = argparse.ArgumentParser(description="MFC discrepancy monitor")
    parser.add_argument("setpoint", nargs="?", type=float, help="MFC setpoint")
    parser.add_argument("actual", nargs="?", type=float, help="MFC actual value")
    args = parser.parse_args()

    if args.setpoint is not None and args.actual is not None:
        monitor(args.setpoint, args.actual)
    elif not sys.stdin.isatty():
        for setpoint, actual in parse_stdin():
            monitor(setpoint, actual)
    else:
        setpoint = os.environ.get("SETPOINT")
        actual = os.environ.get("ACTUAL")
        if setpoint and actual:
            monitor(float(setpoint), float(actual))
        else:
            print("Usage: python mfc_alert.py <setpoint> <actual>", file=sys.stderr)
            print("   or:  SETPOINT=100 ACTUAL=85 python mfc_alert.py", file=sys.stderr)
            print("   or:  echo '100 85' | python mfc_alert.py", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()



