# philoscreen

> *philo* (Greek: love) + *screen* = you love your screen too much.

A passive-aggressive screen time monitor that sends escalating Slack messages to yourself. It starts polite. It does not stay polite.

<p align="center">
  <img src="assets/startup.svg" alt="philoscreen startup" width="560" />
</p>

## Setup (2 minutes)

You need a Mac and a Slack workspace. That's it.

```bash
# 1. Download it
git clone https://github.com/phillipan14/philoscreen.git
cd philoscreen

# 2. Run the setup wizard — it walks you through everything
python3 setup.py
```

The wizard will:
1. Show you exactly how to create a Slack webhook (step by step, with links)
2. Test that your Slack connection works
3. Save your settings securely
4. Optionally set it to start automatically when you open your laptop

**That's it.** No `pip install`. No config files. No terminal wizardry.

> Already have a webhook? You can also just run:
> ```bash
> python3 screen_shame.py --webhook "your-url-here"
> ```

## What happens

Every 60 seconds, philoscreen checks if you're at your computer. When your screen time hits a threshold, it sends you a Slack DM. The tone... escalates.

| Hours | Vibe | Sample message |
|------:|------|----------------|
| **2h** | Polite-ish | *"2 hours. That's fine. Totally fine. Everything is fine. This is fine."* |
| **4h** | Getting personal | *"Your ancestors fought saber-toothed tigers. You're staring at a rectangle."* |
| **6h** | Disappointed parent | *"Your legs are starting to think they're decorative."* |
| **8h** | Genuinely worried | *"Your screen time is now longer than the average person's sleep."* |
| **10h** | Pleading | *"Double digits. There's no trophy for this. There should be an intervention."* |
| **12h** | Full meltdown | *"Your retinas are writing their resignation letter. Your wrists are unionizing."* |

Each tier has **6 randomized messages** so you get a fresh roast every day.

<p align="center">
  <img src="assets/escalation.svg" alt="philoscreen escalation" width="560" />
</p>

## Preview the roasts (no Slack needed)

Want to see what you're signing up for? Run dry-run mode:

```bash
python3 screen_shame.py --dry-run
```

Messages print to your terminal instead of Slack. No setup required.

<p align="center">
  <img src="assets/tier-alert.svg" alt="philoscreen tier alert" width="560" />
</p>

## Make it your own

### Write your own roasts

Open `messages.py` and edit away. Each tier is just a list of strings:

```python
TIERS = {
    2: [
        "Your custom 2-hour roast here.",
        "Get creative. Get personal. Get weird.",
    ],
}
```

### Add or change thresholds

Want a message at 1 hour? Add `1: [...]` to the dict. Want 30-minute check-ins? Go for it.

### Adjust sensitivity

In `screen_shame.py`, two numbers control everything:
- `POLL_INTERVAL` — how often to check (default: 60 seconds)
- `IDLE_THRESHOLD` — how long before you count as "away" (default: 5 minutes)

## How it works (for the curious)

Your Mac tracks how long it's been since you last touched the keyboard or mouse. philoscreen reads this value (`HIDIdleTime` via `ioreg`) every 60 seconds:

- **Touched something in the last 5 minutes?** You're "active." +1 minute to today's total.
- **Haven't touched anything in 5+ minutes?** You're away. Clock pauses.

It resets at midnight. State is saved to a file so restarting won't lose your progress (or re-send messages).

## Uninstall

```bash
# Remove auto-start
python3 setup.py --uninstall

# Or just delete the folder
rm -rf philoscreen
```

## Security

- Your Slack webhook URL is saved locally in `.env` (never committed to git)
- The `.env` file has owner-only permissions (chmod 600)
- philoscreen makes exactly one type of network request: POST to your Slack webhook
- No analytics, no telemetry, no data collection. It's a Python script that roasts you. That's it.

## FAQ

**Q: Does this work on Windows/Linux?**
A: Not yet — it uses a macOS-specific system call. PRs welcome!

**Q: Can I make it meaner?**
A: Edit `messages.py`. There are no limits. Only consequences.

**Q: What if I just... don't open my laptop?**
A: Then you win. That's the whole point.

**Q: Can I use this for my team?**
A: You could. HR might have questions.

## Requirements

- macOS
- Python 3.6+ (comes pre-installed on Mac)
- A Slack workspace (free tier works)

## License

MIT
