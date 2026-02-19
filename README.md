# screen-shame

> Judgment as a Service (JaaS)

A passive-aggressive screen time monitor that sends escalating Slack DMs to yourself based on how long you've been glued to your computer.

Because you won't listen to your mom, your partner, or your optometrist — but maybe you'll listen to a Python script.

<p align="center">
  <img src="assets/startup.svg" alt="screen-shame startup" width="560" />
</p>

## What is this

You know that feeling when you look up from your laptop and it's suddenly dark outside? This is for that.

`screen-shame` monitors your active screen time on macOS and sends you Slack messages that start gentle and end... not gentle. It's like having a concerned friend who lives inside your terminal and has zero chill.

**Zero dependencies.** Just Python 3 and whatever is left of your self-respect.

## The escalation ladder

| Hours | Vibe | Sample |
|------:|------|--------|
| **2h** | "Just checking in :)" | *"2 hours. That's fine. Totally fine. Everything is fine. This is fine."* |
| **4h** | Getting personal | *"Your ancestors fought saber-toothed tigers. You're staring at a rectangle."* |
| **6h** | Disappointed parent | *"Your legs are starting to think they're decorative."* |
| **8h** | Genuinely concerned | *"Your screen time is now longer than the average person's sleep. Think about that."* |
| **10h** | Pleading | *"Double digits. There's no trophy for this. There should be an intervention."* |
| **12h** | Full meltdown | *"Your retinas are writing their resignation letter. Your wrists are unionizing. Your back already left."* |

Each tier has **6 randomized messages** so you get a fresh disappointment every day.

<p align="center">
  <img src="assets/escalation.svg" alt="screen-shame escalation" width="560" />
</p>

## Quick start

### 1. Create a Slack Incoming Webhook

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From scratch**
2. Name it `screen-shame` (or `my-disappointed-mother`, your call)
3. Go to **Incoming Webhooks** → toggle **On**
4. Click **Add New Webhook to Workspace** → pick your DM channel
5. Copy the webhook URL

> **Security note:** Your webhook URL is a secret. Never commit it to git. Use the `SCREEN_SHAME_WEBHOOK` environment variable or pass it via `--webhook`. The `.env` file is already gitignored.

### 2. Run it

```bash
# Clone
git clone https://github.com/phillipan14/screen-shame.git
cd screen-shame

# Test the Slack connection
python3 screen_shame.py --webhook "$SCREEN_SHAME_WEBHOOK" --test

# Run for real
export SCREEN_SHAME_WEBHOOK="your-webhook-url-here"
python3 screen_shame.py
```

### 3. Try it without Slack first

```bash
python3 screen_shame.py --dry-run
```

This prints the roasts to your terminal instead of Slack. Great for previewing the emotional damage before you opt in.

<p align="center">
  <img src="assets/tier-alert.svg" alt="screen-shame tier alert" width="560" />
</p>

## Auto-start on login (macOS)

Want the judgment to begin the moment you open your laptop? Same energy as setting an alarm on a Saturday.

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

# Load it (accept your fate)
launchctl load ~/Library/LaunchAgents/com.screen-shame.plist
```

## How it actually works

On macOS, `ioreg -c IOHIDSystem` exposes `HIDIdleTime` — nanoseconds since your last keyboard/mouse/trackpad input. The script checks every 60 seconds:

- **Idle < 5 min** → you're "active" → +1 minute to the shame counter
- **Idle >= 5 min** → you're away → clock pauses (go you!)

Is it perfect? No. You could be sitting there reading a very long article and it wouldn't count. But let's be honest — you weren't reading an article.

## Customization

### Write your own roasts

Edit `messages.py`. Each tier is a list of strings. Add as many as you want:

```python
TIERS = {
    2: [
        "Your custom 2-hour roast here.",
        "Another way to disappoint yourself at 2 hours.",
    ],
    # ...
}
```

### Change the thresholds

Want to be judged starting at 1 hour? Add `1: [...]` to the `TIERS` dict. We don't kink-shame.

### Adjust sensitivity

In `screen_shame.py`:
- `POLL_INTERVAL` — how often to check (default: 60s)
- `IDLE_THRESHOLD` — seconds before counting as "away" (default: 300s / 5 min)

## Security

- Webhook URLs are **never hardcoded or committed** — use env vars or `--webhook`
- `.env` is gitignored by default
- State file (`~/.screen-shame-state.json`) contains only today's date, minute count, and fired tiers — no credentials
- The script makes exactly one type of outbound request: POST to your Slack webhook. That's it.

## State persistence

State is saved to `~/.screen-shame-state.json`:

- Restarting the script won't re-send today's messages
- Screen time accumulates across restarts
- Resets automatically at midnight (a fresh start you probably don't deserve)

## Requirements

- macOS (uses `ioreg` for idle detection)
- Python 3.6+
- A Slack workspace
- A willingness to be roasted by your own computer

## FAQ

**Q: Can I use this for my team?**
A: You could, but HR might have questions.

**Q: Does it work on Linux?**
A: Not yet. Linux users are already judging themselves enough. (PRs welcome though.)

**Q: Can I make it meaner?**
A: Edit `messages.py`. There are no limits. Only consequences.

**Q: What if I uninstall it?**
A: That's exactly what someone with 10 hours of screen time would say.

## License

MIT — do whatever you want with it. We're not your screen time.
