#!/usr/bin/env python3
"""
screen-shame: A passive-aggressive screen time monitor that sends
escalating Slack DMs based on how long you've been at your computer.

Usage:
    1. Create a Slack Incoming Webhook:
       https://api.slack.com/messaging/webhooks
    2. Set the SCREEN_SHAME_WEBHOOK env var (or pass --webhook)
    3. Run: python3 screen_shame.py

The script polls macOS idle time every 60 seconds. If you've been
active (idle < 5 min), it accumulates screen time. When you cross
a tier threshold (2h, 4h, 6h, ...), it sends you a message.

Resets daily at midnight.
"""

import argparse
import json
import os
import random
import subprocess
import sys
import time
from datetime import datetime, date
from urllib.request import Request, urlopen
from urllib.error import URLError

from messages import TIERS, THRESHOLDS

# ── Config ──────────────────────────────────────────────
POLL_INTERVAL = 60          # seconds between checks
IDLE_THRESHOLD = 300        # seconds — under this counts as "active"
STATE_FILE = os.path.expanduser("~/.screen-shame-state.json")

# ── ANSI Colors ─────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"
BG_RED  = "\033[41m"

# Tier colors — escalating warmth
TIER_COLORS = {
    2:  CYAN,
    4:  YELLOW,
    6:  MAGENTA,
    8:  RED,
    10: f"{BOLD}{RED}",
    12: f"{BOLD}{BG_RED}{WHITE}",
}

BANNER = f"""{BOLD}{MAGENTA}
  ┌─────────────────────────────────────────┐
  │                                         │
  │   {WHITE}screen-shame{MAGENTA}                        │
  │   {DIM}{WHITE}passive-aggressive screen monitor{RESET}{BOLD}{MAGENTA}  │
  │                                         │
  └─────────────────────────────────────────┘{RESET}
"""

SHUTDOWN_MSG = f"""
{DIM}─────────────────────────────────────────────{RESET}
  {GREEN}screen-shame stopped.{RESET}
  {DIM}Your eyes thank you.{RESET}
{DIM}─────────────────────────────────────────────{RESET}
"""


def log(msg: str, color: str = DIM):
    """Print a timestamped, styled log line."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"  {DIM}{ts}{RESET}  {color}{msg}{RESET}")


def get_idle_seconds() -> float:
    """Read macOS HIDIdleTime from ioreg (nanoseconds → seconds)."""
    try:
        output = subprocess.check_output(
            ["ioreg", "-c", "IOHIDSystem", "-d", "4"],
            text=True,
        )
        for line in output.splitlines():
            if "HIDIdleTime" in line and "=" in line:
                raw = line.split("=")[-1].strip()
                return int(raw) / 1_000_000_000
    except (subprocess.CalledProcessError, ValueError):
        pass
    return 0.0


def send_slack_message(webhook_url: str, text: str) -> bool:
    """Post a message to a Slack Incoming Webhook."""
    payload = json.dumps({"text": text}).encode("utf-8")
    req = Request(webhook_url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req) as resp:
            return resp.status == 200
    except URLError as e:
        log(f"Slack send failed: {e}", RED)
        return False


def load_state() -> dict:
    """Load persisted state (survives restarts within the same day)."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                state = json.load(f)
            if state.get("date") == str(date.today()):
                return state
        except (json.JSONDecodeError, KeyError):
            pass
    return {"date": str(date.today()), "active_minutes": 0, "fired_tiers": []}


def save_state(state: dict):
    """Persist state to disk."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def pick_message(tier: int) -> str:
    """Pick a random message for the given tier."""
    return random.choice(TIERS[tier])


def format_time(minutes: int) -> str:
    """Format minutes into a human-readable string."""
    hours = minutes // 60
    mins = minutes % 60
    if hours and mins:
        return f"{hours}h {mins}m"
    elif hours:
        return f"{hours}h"
    return f"{mins}m"


def progress_bar(active_minutes: int, width: int = 24) -> str:
    """Render a visual progress bar toward the next tier."""
    active_hours = active_minutes / 60
    # Find the next unfired tier
    next_tier = None
    for t in THRESHOLDS:
        if active_hours < t:
            next_tier = t
            break
    if next_tier is None:
        return f"{RED}{'█' * width}{RESET} {DIM}MAX{RESET}"

    prev_tier = 0
    for t in THRESHOLDS:
        if t < next_tier:
            prev_tier = t
    progress = (active_hours - prev_tier) / (next_tier - prev_tier)
    filled = int(progress * width)
    bar = f"{'█' * filled}{'░' * (width - filled)}"

    color = TIER_COLORS.get(next_tier, WHITE)
    return f"{color}{bar}{RESET} {DIM}{next_tier}h{RESET}"


def render_status(state: dict, idle: float):
    """Print a compact, aligned status line."""
    mins = state["active_minutes"]
    bar = progress_bar(mins)
    active_str = format_time(mins)
    idle_str = f"{idle:.0f}s"
    status = "active" if idle < IDLE_THRESHOLD else "idle"
    status_color = GREEN if idle < IDLE_THRESHOLD else YELLOW

    print(
        f"  {BOLD}{WHITE}{active_str:>7}{RESET}"
        f"  {bar}"
        f"  {status_color}● {status:<6}{RESET}"
        f"  {DIM}idle {idle_str}{RESET}",
        end="\r",
    )


def print_startup(state: dict, dry_run: bool):
    """Print startup info block."""
    print(BANNER)
    mode = f"{YELLOW}dry run{RESET}" if dry_run else f"{GREEN}live → Slack{RESET}"
    active = format_time(state["active_minutes"])
    fired = ", ".join(f"{t}h" for t in state["fired_tiers"]) or "none"

    print(f"  {DIM}{'─' * 43}{RESET}")
    print(f"  {DIM}mode{RESET}      {mode}")
    print(f"  {DIM}active{RESET}    {BOLD}{active}{RESET}")
    print(f"  {DIM}fired{RESET}     {fired}")
    print(f"  {DIM}polling{RESET}   every {POLL_INTERVAL}s")
    print(f"  {DIM}idle ≥{RESET}    {IDLE_THRESHOLD}s counts as away")
    print(f"  {DIM}{'─' * 43}{RESET}")
    print()


def print_tier_alert(threshold: int, msg: str, dry_run: bool):
    """Print a beautifully formatted tier alert in the terminal."""
    color = TIER_COLORS.get(threshold, WHITE)
    label = "DRY RUN" if dry_run else "SENT"

    print()
    print(f"  {color}{'━' * 43}{RESET}")
    print(f"  {color}{BOLD}  ⚡ TIER {threshold}h{RESET}  {DIM}[{label}]{RESET}")
    print(f"  {color}{'─' * 43}{RESET}")
    # Word-wrap the message to ~39 chars
    words = msg.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= 39:
            current = f"{current} {word}" if current else word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    for line in lines:
        print(f"  {color}  {line}{RESET}")
    print(f"  {color}{'━' * 43}{RESET}")
    print()


def run(webhook_url: str, dry_run: bool = False):
    """Main loop: poll idle time, accumulate active minutes, fire messages."""
    state = load_state()
    print_startup(state, dry_run)

    while True:
        # Reset at midnight
        if str(date.today()) != state["date"]:
            log("New day — resetting counters", CYAN)
            state = {"date": str(date.today()), "active_minutes": 0, "fired_tiers": []}
            print()

        idle = get_idle_seconds()

        if idle < IDLE_THRESHOLD:
            state["active_minutes"] += 1

        active_hours = state["active_minutes"] / 60

        # Check if we crossed a new tier
        for threshold in THRESHOLDS:
            if active_hours >= threshold and threshold not in state["fired_tiers"]:
                msg = pick_message(threshold)
                timestamp = datetime.now().strftime("%I:%M %p")
                slack_msg = (
                    f":eyes: *Screen Time Alert — {format_time(state['active_minutes'])}*\n\n"
                    f"{msg}\n\n"
                    f"_sent at {timestamp} by screen-shame_"
                )

                if dry_run:
                    print_tier_alert(threshold, msg, dry_run=True)
                else:
                    sent = send_slack_message(webhook_url, slack_msg)
                    if sent:
                        print_tier_alert(threshold, msg, dry_run=False)
                    else:
                        log(f"Failed to send tier {threshold}h — will retry", RED)
                        continue

                state["fired_tiers"].append(threshold)

        save_state(state)
        render_status(state, idle)
        time.sleep(POLL_INTERVAL)


def print_test_success():
    """Print a nice test success message."""
    print()
    print(f"  {GREEN}{'━' * 43}{RESET}")
    print(f"  {GREEN}{BOLD}  ✓ Test message sent!{RESET}")
    print(f"  {DIM}  Check your Slack DMs.{RESET}")
    print(f"  {GREEN}{'━' * 43}{RESET}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Passive-aggressive screen time monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
examples:
  %(prog)s --dry-run              Run locally, print messages to terminal
  %(prog)s --webhook URL          Run with Slack integration
  %(prog)s --webhook URL --test   Send a test message and exit
        """,
    )
    parser.add_argument("--webhook", help="Slack Incoming Webhook URL")
    parser.add_argument("--dry-run", action="store_true", help="Print messages to stdout instead of Slack")
    parser.add_argument("--test", action="store_true", help="Send a single test message and exit")
    args = parser.parse_args()

    webhook_url = args.webhook or os.environ.get("SCREEN_SHAME_WEBHOOK", "")

    if args.test:
        if not webhook_url:
            print(f"\n  {RED}Error: provide --webhook or set SCREEN_SHAME_WEBHOOK{RESET}\n", file=sys.stderr)
            sys.exit(1)
        msg = ":wave: *screen-shame test* — If you're reading this, the roasting pipeline is operational."
        if send_slack_message(webhook_url, msg):
            print_test_success()
        else:
            print(f"\n  {RED}Failed to send test message.{RESET}\n", file=sys.stderr)
            sys.exit(1)
        return

    if not webhook_url and not args.dry_run:
        print(f"\n  {RED}Error:{RESET} provide --webhook URL or set SCREEN_SHAME_WEBHOOK")
        print(f"  {DIM}Or use --dry-run to test without Slack.{RESET}\n")
        sys.exit(1)

    try:
        run(webhook_url, dry_run=args.dry_run)
    except KeyboardInterrupt:
        print(SHUTDOWN_MSG)


if __name__ == "__main__":
    main()
