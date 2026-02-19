"""
Passive-aggressive message bank, organized by escalation tier.
Each tier is a list — the script picks one at random so it doesn't repeat.
"""

TIERS = {
    2: [
        "Hey! Just noticed you've been at your screen for 2 hours. No big deal. Just... keeping track. For science.",
        "2 hours in. I'm sure you've been super productive. I believe in you. Mostly.",
        "Quick check-in: 2 hours of screen time. Have you blinked recently? Just wondering.",
        "2 hours. That's fine. Totally fine. Everything is fine.",
    ],
    4: [
        "4 hours. Cool cool cool. I'm sure it's all very important work and definitely not doomscrolling.",
        "Fun fact: you've been staring at a glowing rectangle for 4 hours. Your ancestors fought bears. Just saying.",
        "4 hours of screen time. You know what takes 4 hours? Hiking a mountain. Learning to cook risotto. Just throwing that out there.",
        "Wow, 4 hours already? Time flies when you're... sitting completely still... staring at light...",
    ],
    6: [
        "6 hours. Six. Your eyes called. They'd like to see something that isn't backlit.",
        "Half a waking day. On a screen. I'm not mad, I'm just disappointed. Actually no, I'm a little mad.",
        "6 hours. At this point your chair has more of a relationship with you than most humans do.",
        "You've hit 6 hours. The sun exists, btw. It's that bright thing outside. You might remember it.",
    ],
    8: [
        "8 hours. A full workday of screen time. Except we both know at least 2 of those hours weren't work.",
        "At 8 hours, your screen isn't a tool anymore. It's a lifestyle. A concerning one.",
        "8 hours in. At what point does the screen start using you? Asking for a friend.",
        "Congratulations on 8 hours! That's almost impressive if it weren't so deeply sad.",
    ],
    10: [
        "10 hours. I've run out of clever things to say. Please go outside. I'm literally begging you.",
        "TEN. HOURS. Even your laptop is tired of you. I can hear the fan crying.",
        "10 hours of screen time. This isn't a flex. This is a cry for help. YOUR cry for help.",
        "You've been here 10 hours. I'm going to start sending these every 5 minutes until you stop.",
    ],
    12: [
        "12 hours. I'm calling this what it is: a hostage situation. Blink twice if you need help.",
        "Twelve hours. TWELVE. I'm genuinely worried about you. When did you last see the sky?",
        "12 hours in. Your screen-to-life ratio is now officially concerning. Even by tech bro standards.",
        "At 12 hours, I'm no longer passive-aggressive. I'm just aggressive. GO. OUTSIDE. NOW.",
    ],
}

# Thresholds in order for the tracker to iterate through
THRESHOLDS = sorted(TIERS.keys())
