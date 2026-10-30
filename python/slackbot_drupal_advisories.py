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

report_date = datetime.now().strftime("%m/%d/%y %H:%M")

messages = [
    ":mega::drupal-2: *DRUPAL SECURITY ADVISORIES- :closed_lock_with_key::drupalbot:",
    f"From the last 7 days. _Report generated: {report_date}_",
    ""
]

for name, rss_url in FEEDS.items():

    feed = feedparser.parse(rss_url)
    feed_messages = []

    # Log an error if the feed isn't landing, Drupal.org is down, etc.
    status = feed.get("status")

    if status is None or status >= 400:
        raise RuntimeError(
            f"Failed to fetch Drupal {name} RSS feed: HTTP {status}"
        )

    # Trip a runtime error if the feed is malformed.
    if feed.get("bozo"):
        raise RuntimeError(f"Invalid RSS feed: {feed.bozo_exception}")

    # Log an error if the feed isn't loading, Drupal.org is down, etc.
    if feed.get("status", 200) >= 400:
        raise RuntimeError(f"Failed to fetch Drupal {name} RSS feed")

    # Trip a runtime error if the feed is malformed.
    if feed.get("bozo"):
        raise RuntimeError(f"Invalid RSS feed: {feed.bozo_exception}")

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
            project, separator, details = entry.title.partition(" - ")
            severity = details.split (" - ") [0]
            if separator:
                feed_messages.append(
                    f":small_blue_diamond: *{project}* - <{entry.link}|{severity}>"
                )
            else:
                feed_messages.append(
                    f":small_blue_diamond: <{entry.link}|{entry.title}>"
                )
    count = len(feed_messages)

    messages.append(f"*{count} {name.upper()} Updates*")

    if feed_messages:
        messages.extend(feed_messages)
    else:
        messages.append("_No new advisories._")

    messages.append("")

# Ship the advisory message to slack
if messages:
    post_to_slack("\n".join(messages))
