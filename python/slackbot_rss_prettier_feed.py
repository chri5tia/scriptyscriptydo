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
Requires Python 3 and feedparser (pip install feedparser).

.·:* We want the Drupal advisories in slack to be pretty and simple. *:·.

"""

# Grab some modules
import feedparser
import json
import os
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen

# Calculate cut off, 7 days ago.
# We can change days=7 to hours=24.
cutoff = datetime.now(timezone.utc) - timedelta(days=7)

# Loop through the feeds.
# This is where we could add more if ever needed.
FEEDS = {
    "core": "https://www.drupal.org/security/rss.xml",
    "contrib": "https://www.drupal.org/security/contrib/rss.xml",
}

def post_to_slack(message):
    """Send a message to Slack using an incoming webhook."""
    webhook_url = os.environ["SLACK_WEBHOOK_URL"]

    payload = json.dumps({"text": message}).encode("utf-8")

    request = Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=15) as response:
        if response.status !=200:
            raise RuntimeError(f"Slack Returned HTTP {response.status}")

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
            message = (f"<{entry.link}|{entry.title}>")
            print(message)
            post_to_slack(message)
            # Uncomment the below during integration testing to avoid flooding the channel
            # break