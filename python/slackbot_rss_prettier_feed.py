#!/usr/bin/env python3

"""
 ────────◢◣◥◤ ✨ ℂ𝕐𝔹𝔼ℝ𝕊ℙ𝔸ℂ𝔼 ✨ ◥◤◢◣────────
 ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
╔══════════════════════════════════════════╗
║ ░░░░░░ PRETTIER RSS FEED SLACKBOT ░░░░░░ ║
║ 🔺▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼ 🔺 ║
║ >> Posting Drupal security advisories... ║
╚══════════════════════════════════════════╝
▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

Uses python's feedparser module to parse given RSS feed URLS each day.
Grabs the <pubdate> and <link> items from the RSS feed content.
Uses the datetime module to strip out older advisories.
.·:* We want the Drupal advisories in slack to be pretty and simple. *:·.

"""

# Grab some modules
import feedparser
from datetime import datetime, timedelta, timezone

# Calculate cut off, 7 days ago.
cutoff = datetime.now(timezone.utc) - timedelta(days=7)

# Loop through the feeds, this is where you add more.
FEEDS = {
    "core": "https://www.drupal.org/security/rss.xml",
    "contrib": "https://www.drupal.org/security/contrib/rss.xml",
}

for name, rss_url in FEEDS.items():
    print(f"\n{name.upper()} SECURITY ADVISORIES")

    feed = feedparser.parse(rss_url)

    # Loop through each advisory.
    for entry in feed.entries:

        # Skip entries without publication dates.
        if not hasattr(entry, "published_parsed"):
            continue

         # Convert publication date into a datetime object.
        published = datetime(
             *entry.published_parsed[:6],
             tzinfo=timezone.utc
         )

        # Display advisories published in the last 7 days
        if published >= cutoff:
            print(entry.link, entry.published)
