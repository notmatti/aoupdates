"""Sopel module for tracking GitHub issues

This module tracks issues for a given GitHub repository and
sends notices if a new issue has been submitted.

https://sopel.chat
https://github.com/AniDevTwitter/animeopenings
"""
import sys
import time
import traceback
import json
import urllib.request

from sopel import module

__title__ = 'aogithub'
__version__ = '1.0'
__author__ = 'Matthias Adamczyk'
__email__ = 'mail@notmatti.me'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2017 Matthias Adamczyk'

### CONFIGURATION
GITHUB_API_TOKEN = "" # optional
"""Without a personal access token, GitHub limits the use of the API to 60 request per hour."""
INTERVAL_SECONDS = 60
"""Interval in seconds to check for new issues"""
CHANNELS = []
"""If you don't want to send notices to all channels sopel joined,
specify here the channel(s) you want.
"""
REPO_USER = "AniDevTwitter"
"""The username of the repository to be checked"""
REPO_NAME = "animeopenings"
"""The name of the repository to be checked"""
###

issue_number = 0

def send_notice(bot, message):
    """Send an IRC NOTICE"""
    global CHANNELS

    if not CHANNELS:
        CHANNELS = bot.channels
    for channel in CHANNELS:
        bot.notice(message, dest=channel)


def api_request(token=""):
    """Form an API request"""
    url = "https://api.github.com/repos/{}/{}/issues?state=all".format(REPO_USER, REPO_NAME)

    if token:
        request = urllib.request.Request(url, None, {'Authorization': 'token {}'.format(token)})
        return urllib.request.urlopen(request).read().decode("utf-8")

    return urllib.request.urlopen(url).read().decode("utf-8")


def setup(bot):
    """Get the latest issue number from the repository"""
    global issue_number
    r = api_request(GITHUB_API_TOKEN)
    for item in json.loads(r):
        if "number" in item and item["number"] > issue_number:
            issue_number = item["number"]


@module.interval(INTERVAL_SECONDS)
def check_github(bot):
    """Check for new issues on GitHub and send an IRC notice when a new
    issue or pull request has been submitted
    """
    global issue_number
    # Do not check for new issues if the bot is not connected to any channel
    if not bool(bot.channels):
        return

    try:
        r = api_request(GITHUB_API_TOKEN)
        for item in json.loads(r):
            if item["number"] > issue_number:
                issue_number = item["number"]
                if "pull_request" in item:
                    send_notice(bot, "New Pull Request: \"{}\" {}".format(
                        item["title"], item["html_url"]))
                else:
                    send_notice(bot, "New Issue: \"{}\" {}".format(
                        item["title"], item["html_url"]))
                time.sleep(1)
    except:
        traceback.print_exc(file=sys.stdout)
