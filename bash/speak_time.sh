#!/bin/bash

# Word bank of random phrases
phrases=(
    "Drink water!"
    "You're doing great. Keep it up!"
    "Focus on one thing at a time!"
    "Be a good person!"
    "Focus on the task at hand!"
    "Good job on your pullups today."
    "Great job, Hamstray!"
)

# Get the current time
current_time=$(date '+%I:%M %p')

# Select a random phrase
random_phrase=${phrases[RANDOM % ${#phrases[@]}]}

# Speak the time and the random phrase
say "The current time is $current_time. $random_phrase"

