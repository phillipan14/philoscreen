#!/usr/bin/env python3
"""
philoscreen setup wizard.

Run this once to get everything configured:
    python3 setup.py

It will:
  1. Walk you through creating a Slack webhook (with a link)
  2. Save your webhook URL securely to a .env file
  3. Test the connection
  4. Optionally set up auto-start on login
  5. Show you how to run it
"""

import json
import os
import subprocess
import sys
import textwrap
from urllib.request import Request, urlopen
from urllib.error import URLError

# ── Paths ───────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(SCRIPT_DIR, ".env")
PLIST_PATH = os.path.expanduser("~/Library/LaunchAgents/com.philoscreen.plist")
MAIN_SCRIPT = os.path.join(SCRIPT_DIR, "screen_shame.py")

# ── Colors ──────────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
CYAN    = "\033[36m"
MAGENTA = "\033[35m"
WHITE   = "\033[37m"


def clear():
    subprocess.run(["clear"], check=False)


def header(title: str):
    print()
    print(f"  {MAGENTA}{BOLD}{'─' * 45}{RESET}")
    print(f"  {MAGENTA}{BOLD}  {title}{RESET}")
    print(f"  {MAGENTA}{BOLD}{'─' * 45}{RESET}")
    print()


def step(num: int, total: int, text: str):
    print(f"  {CYAN}{BOLD}[{num}/{total}]{RESET}  {text}")
    print()


def success(text: str):
    print(f"  {GREEN}{BOLD}  ✓  {text}{RESET}")


def fail(text: str):
    print(f"  {RED}{BOLD}  ✗  {text}{RESET}")


def info(text: str):
    print(f"  {DIM}  {text}{RESET}")


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"  {BOLD}  → {prompt}{suffix}: {RESET}").strip()
    except (EOFError, KeyboardInterrupt):
        print(f"\n\n  {DIM}Setup cancelled. Run python3 setup.py anytime to try again.{RESET}\n")
        sys.exit(0)
    return answer or default


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    try:
        answer = input(f"  {BOLD}  → {prompt} [{hint}]: {RESET}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print(f"\n\n  {DIM}Setup cancelled. Run python3 setup.py anytime to try again.{RESET}\n")
        sys.exit(0)
    if not answer:
        return default
    return answer in ("y", "yes")


def test_webhook(url: str) -> bool:
    payload = json.dumps({
        "text": ":wave: *philoscreen test* — If you're reading this, setup worked! The roasting pipeline is operational."
    }).encode("utf-8")
    req = Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req) as resp:
            return resp.status == 200
    except (URLError, Exception):
        return False


def save_env(webhook_url: str):
    with open(ENV_FILE, "w") as f:
        f.write(f"PHILOSCREEN_WEBHOOK={webhook_url}\n")
    os.chmod(ENV_FILE, 0o600)  # read/write only for owner


def load_env() -> str:
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                if line.startswith("PHILOSCREEN_WEBHOOK="):
                    return line.split("=", 1)[1].strip()
    return ""


def install_launchd(webhook_url: str):
    plist = textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
            "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>Label</key>
            <string>com.philoscreen</string>
            <key>ProgramArguments</key>
            <array>
                <string>/usr/bin/python3</string>
                <string>{MAIN_SCRIPT}</string>
            </array>
            <key>EnvironmentVariables</key>
            <dict>
                <key>PHILOSCREEN_WEBHOOK</key>
                <string>{webhook_url}</string>
            </dict>
            <key>RunAtLoad</key>
            <true/>
            <key>KeepAlive</key>
            <true/>
            <key>StandardOutPath</key>
            <string>/tmp/philoscreen.log</string>
            <key>StandardErrorPath</key>
            <string>/tmp/philoscreen.log</string>
        </dict>
        </plist>""")

    os.makedirs(os.path.dirname(PLIST_PATH), exist_ok=True)
    with open(PLIST_PATH, "w") as f:
        f.write(plist)

    subprocess.run(["launchctl", "unload", PLIST_PATH],
                   capture_output=True, check=False)
    result = subprocess.run(["launchctl", "load", PLIST_PATH],
                            capture_output=True, check=False)
    return result.returncode == 0


def uninstall_launchd():
    if os.path.exists(PLIST_PATH):
        subprocess.run(["launchctl", "unload", PLIST_PATH],
                       capture_output=True, check=False)
        os.remove(PLIST_PATH)


def main():
    clear()
    print(f"""{BOLD}{MAGENTA}
  ┌─────────────────────────────────────────┐
  │                                         │
  │   {WHITE}philoscreen{MAGENTA}  {DIM}{WHITE}setup wizard{RESET}{BOLD}{MAGENTA}          │
  │                                         │
  │   {DIM}{WHITE}Let's get you roasted in 2 minutes.{RESET}{BOLD}{MAGENTA}  │
  │                                         │
  └─────────────────────────────────────────┘{RESET}
""")

    existing = load_env()
    if existing:
        info(f"Found existing webhook in .env")
        if ask_yes_no("Use the existing webhook URL?"):
            webhook_url = existing
        else:
            webhook_url = ""
    else:
        webhook_url = ""

    # ── Step 1: Get webhook URL ──────────────────────────
    if not webhook_url:
        step(1, 4, "Create a Slack Incoming Webhook")
        print(f"  {WHITE}  You need a Slack webhook URL. Here's how to get one:{RESET}")
        print()
        print(f"  {BOLD}  1.{RESET} Open this link in your browser:")
        print(f"  {CYAN}     https://api.slack.com/apps{RESET}")
        print()
        print(f"  {BOLD}  2.{RESET} Click {BOLD}Create New App{RESET} → {BOLD}From scratch{RESET}")
        print(f"     Name it anything (e.g., \"philoscreen\")")
        print(f"     Pick your Slack workspace")
        print()
        print(f"  {BOLD}  3.{RESET} In the left sidebar, click {BOLD}Incoming Webhooks{RESET}")
        print(f"     Toggle it {GREEN}{BOLD}ON{RESET}")
        print()
        print(f"  {BOLD}  4.{RESET} Scroll down, click {BOLD}Add New Webhook to Workspace{RESET}")
        print(f"     Choose your own DM channel (messages to yourself)")
        print()
        print(f"  {BOLD}  5.{RESET} Copy the webhook URL (starts with https://hooks.slack.com/...)")
        print()

        while True:
            webhook_url = ask("Paste your webhook URL here")
            if webhook_url.startswith("https://hooks.slack.com/"):
                break
            elif webhook_url == "":
                print(f"  {DIM}  No URL entered. Take your time — the link above will help.{RESET}")
            else:
                print(f"  {YELLOW}  That doesn't look like a Slack webhook URL.{RESET}")
                print(f"  {DIM}  It should start with: https://hooks.slack.com/services/...{RESET}")
                print()
    else:
        step(1, 4, "Webhook URL")
        info(f"Using saved webhook: ...{webhook_url[-20:]}")

    # ── Step 2: Test the connection ──────────────────────
    print()
    step(2, 4, "Testing Slack connection...")
    print(f"  {DIM}  Sending a test message to your Slack...{RESET}")
    print()

    if test_webhook(webhook_url):
        success("Test message sent! Check your Slack DMs.")
        print()
    else:
        fail("Couldn't reach Slack.")
        print(f"  {DIM}  Double-check your webhook URL and try again.{RESET}")
        print(f"  {DIM}  Run: python3 setup.py{RESET}")
        print()
        sys.exit(1)

    # ── Step 3: Save the webhook URL ─────────────────────
    step(3, 4, "Saving your webhook URL")
    save_env(webhook_url)
    success(f"Saved to .env (permissions: owner-only, gitignored)")
    print()

    # ── Step 4: Auto-start option ────────────────────────
    step(4, 4, "Auto-start on login (optional)")
    print(f"  {WHITE}  Want philoscreen to start automatically{RESET}")
    print(f"  {WHITE}  every time you open your laptop?{RESET}")
    print()

    if ask_yes_no("Enable auto-start?"):
        if install_launchd(webhook_url):
            success("Auto-start enabled! philoscreen is now running.")
            info("It will start automatically on every login.")
            info("Logs: /tmp/philoscreen.log")
        else:
            fail("Couldn't install auto-start. You can set it up manually later.")
    else:
        info("Skipped. You can always enable it later by running setup again.")

    # ── Done! ────────────────────────────────────────────
    print()
    print(f"  {GREEN}{BOLD}{'━' * 45}{RESET}")
    print(f"  {GREEN}{BOLD}  Setup complete! You're ready to be judged.{RESET}")
    print(f"  {GREEN}{BOLD}{'━' * 45}{RESET}")
    print()
    print(f"  {WHITE}  To run manually:{RESET}")
    print(f"  {CYAN}    python3 {MAIN_SCRIPT}{RESET}")
    print()
    print(f"  {WHITE}  To preview the roasts (no Slack):{RESET}")
    print(f"  {CYAN}    python3 {MAIN_SCRIPT} --dry-run{RESET}")
    print()
    print(f"  {WHITE}  To uninstall auto-start:{RESET}")
    print(f"  {CYAN}    python3 setup.py --uninstall{RESET}")
    print()
    info("Your webhook URL is saved in .env (never committed to git).")
    info("Happy judging!")
    print()


def handle_uninstall():
    clear()
    header("Uninstall auto-start")
    if os.path.exists(PLIST_PATH):
        uninstall_launchd()
        success("Auto-start removed. philoscreen will no longer run on login.")
    else:
        info("Auto-start wasn't enabled. Nothing to remove.")

    if os.path.exists(ENV_FILE):
        if ask_yes_no("Also delete saved webhook URL (.env)?", default=False):
            os.remove(ENV_FILE)
            success("Webhook URL removed.")
        else:
            info("Kept .env file.")
    print()


if __name__ == "__main__":
    if "--uninstall" in sys.argv:
        handle_uninstall()
    else:
        main()
