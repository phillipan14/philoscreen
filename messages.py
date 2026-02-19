"""
Passive-aggressive message bank, organized by escalation tier.
Each tier is a list — the script picks one at random so you get
a fresh disappointment every time.

Feel free to add your own. The more specific the guilt, the better.
"""

TIERS = {
    2: [
        "Hey! Just noticed you've been at your screen for 2 hours. No big deal. Just... keeping track. For science.",
        "2 hours in. I'm sure you've been super productive. I believe in you. Mostly.",
        "Quick check-in: 2 hours of screen time. Have you blinked recently? Genuinely asking.",
        "2 hours. That's fine. Totally fine. Everything is fine. This is fine.",
        "Fun fact: 2 hours ago you sat down to 'quickly check one thing.'",
        "2 hours! That's like... an entire movie. Did you at least enjoy it? No? Cool.",
    ],
    4: [
        "4 hours. Cool cool cool. I'm sure it's all very important work and definitely not doomscrolling.",
        "Fun fact: you've been staring at a glowing rectangle for 4 hours. Your ancestors fought saber-toothed tigers. Just saying.",
        "4 hours of screen time. You know what takes 4 hours? Hiking a mountain. Learning pottery. Having a personality. Just throwing that out there.",
        "Wow, 4 hours already? Time flies when you're... sitting completely still... staring at light... like a moth.",
        "4 hours. Your posture called. It's filing a missing persons report for your spine.",
        "You've been here 4 hours. Somewhere, a park bench is gathering dust that has your name on it.",
    ],
    6: [
        "6 hours. Six. Your eyes called. They'd like to see something that isn't backlit. Literally anything.",
        "Half a waking day. On a screen. I'm not mad, I'm just disappointed. Actually no, I'm a little mad.",
        "6 hours. At this point your chair has more of a relationship with you than most humans do.",
        "You've hit 6 hours. The sun exists, btw. It's that bright thing outside. You might remember it from childhood.",
        "6 hours in and I bet you haven't even stood up. Your legs are starting to think they're decorative.",
        "Do you know what vitamin D deficiency looks like? Because 6 hours of this is how you find out.",
    ],
    8: [
        "8 hours. A full workday of screen time. Except we both know at least 3 of those hours weren't work. Don't lie to me.",
        "At 8 hours, your screen isn't a tool anymore. It's a lifestyle. A sad, backlit lifestyle.",
        "8 hours in. At what point does the screen start using you? Asking for a friend. That friend is your optometrist.",
        "Congratulations on 8 hours! That's almost impressive. If it weren't so deeply, profoundly sad.",
        "8 hours. Doctors recommend 30 minutes of exercise a day. You've done 480 minutes of... this.",
        "Your screen time today is now longer than the average person's sleep. Think about that. Then go to bed.",
    ],
    10: [
        "10 hours. I've run out of clever things to say. Please go outside. I'm literally begging you.",
        "TEN. HOURS. Even your laptop is tired of you. I can hear the fans crying. Real tears. Liquid cooling.",
        "10 hours of screen time. This isn't a flex. This is a cry for help. YOUR cry for help. I'm just the messenger.",
        "You've been here 10 hours. I'm going to start sending these every 5 minutes until you stop. Don't test me.",
        "10 hours. At this point I'm not even passive-aggressive. I'm just worried. Like, genuinely. Are you okay?",
        "Double digits! You hit double-digit screen time. There's no trophy for this. There should be an intervention.",
    ],
    12: [
        "12 hours. I'm calling this what it is: a hostage situation. Blink twice if you need help.",
        "Twelve hours. TWELVE. I'm genuinely worried about you. When did you last see the sky? Do you remember its color?",
        "12 hours in. Your screen-to-life ratio is now medically concerning. Even by tech bro standards. Even by THEIR standards.",
        "At 12 hours, I'm no longer passive-aggressive. I'm just aggressive. GO. OUTSIDE. NOW. I'm not kidding.",
        "12 hours. Your retinas are writing their resignation letter. Your wrists are unionizing. Your back already left.",
        "Congratulations, you've unlocked: Existential Dread. 12 hours. What are we doing here? What is life?",
    ],
}

# Thresholds in order for the tracker to iterate through
THRESHOLDS = sorted(TIERS.keys())
