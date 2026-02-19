# screen-shame

A passive-aggressive screen time monitor that sends escalating Slack DMs to yourself based on how long you've been at your computer.

Because sometimes you need someone to judge you — and that someone is a Python script.

<p align="center">
  <img src="assets/startup.svg" alt="screen-shame startup" width="560" />
</p>

## How it works

1. Polls macOS idle time every 60 seconds via `ioreg`
2. If idle < 5 minutes → counts as "active" screen time
3. Accumulates active minutes throughout the day
4. Sends a Slack DM when you cross a tier threshold
5. Resets at midnight

**Zero dependencies** — just Python 3 and the standard library. No `pip install` needed.

## The tiers

| Hours | Vibe | Example |
|------:|------|---------|
| **2h** | Gentle nudge | *"2 hours. That's fine. Totally fine. Everything is fine."* |
| **4h** | Getting snarky | *"Your ancestors fought bears. You're staring at a rectangle."* |
| **6h** | Disappointed | *"Your chair has more of a relationship with you than most humans."* |
| **8h** | Concerned | *"At what point does the screen start using you?"* |
| **10h** | Begging | *"I've run out of clever things to say. Please go outside."* |
| **12h** | Nuclear | *"I'm no longer passive-aggressive. I'm just aggressive. GO. OUTSIDE."* |

Each tier has 4 randomized messages so it doesn't repeat.

<p align="center">
  <img src="assets/escalation.svg" alt="screen-shame escalation" width="560" />
</p>

## Quick start

### 1. Create a Slack Incoming Webhook

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From scratch**
2. Name it `screen-shame`, pick your workspace
3. Go to **Incoming Webhooks** → toggle **On**
4. Click **Add New Webhook to Workspace** → pick your DM channel
5. Copy the webhook URL

### 2. Run it

```bash
# Clone
git clone https://github.com/phillipan14/screen-shame.git
cd screen-shame

# Test the Slack connection
python3 screen_shame.py --webhook "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" --test

# Run for real
python3 screen_shame.py --webhook "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Or set it as an environment variable
export SCREEN_SHAME_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
python3 screen_shame.py
```

### 3. Try it without Slack first

```bash
python3 screen_shame.py --dry-run
```

This prints messages to your terminal instead of Slack — great for previewing the roasts.

<p align="center">
  <img src="assets/tier-alert.svg" alt="screen-shame tier alert" width="560" />
</p>

## Auto-start on login (macOS)

Create a Launch Agent so screen-shame runs automatically:

```bash
cat > ~/Library/LaunchAgents/com.screen-shame.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.screen-shame</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/screen-shame/screen_shame.py</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>SCREEN_SHAME_WEBHOOK</key>
        <string>YOUR_WEBHOOK_URL_HERE</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Load it
launchctl load ~/Library/LaunchAgents/com.screen-shame.plist
```

## How it detects screen time

On macOS, `ioreg -c IOHIDSystem` exposes `HIDIdleTime` — the nanoseconds since the last keyboard, mouse, or trackpad input. The script checks this every 60 seconds:

- **Idle < 5 minutes** → you're "active" → +1 minute to today's total
- **Idle ≥ 5 minutes** → you're away → clock pauses

This is the same signal macOS uses for screen saver activation. It's not perfect (you could be reading), but it's accurate enough for the purpose of judging you.

## Customization

### Add your own messages

Edit `messages.py` — each tier is a list of strings. The script picks one at random:

```python
TIERS = {
    2: [
        "Your custom 2-hour message here.",
        "Another option for 2 hours.",
    ],
    # ...
}
```

### Change tier thresholds

Edit the keys in `TIERS`. Want a message at 1 hour? Add `1: [...]`.

### Adjust sensitivity

In `screen_shame.py`:
- `POLL_INTERVAL` — how often to check (default: 60s)
- `IDLE_THRESHOLD` — seconds of inactivity before you count as "away" (default: 300s)

## State persistence

The script saves its state to `~/.screen-shame-state.json`. This means:

- Restarting the script mid-day won't re-send messages
- Screen time accumulates even across restarts
- State resets automatically at midnight

## Requirements

- macOS (uses `ioreg` for idle time detection)
- Python 3.6+
- A Slack workspace with an Incoming Webhook

## License

MIT
