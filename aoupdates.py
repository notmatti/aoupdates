"""Sopel module for tracking changes at https://openings.moe

This module checks for new videos on https://openings.moe and
notifies the channel if new videos have been published.

https://sopel.chat
https://github.com/AniDevTwitter/animeopenings
"""
import sys
import os
import time
import traceback
import json
import urllib.request

from sopel import module

__title__ = 'aoupdates'
__version__ = '1.0'
__author__ = 'Matthias Adamczyk'
__email__ = 'mail@notmatti.me'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2017 Matthias Adamczyk'

### CONFIGURATION
CHANNELS = []
"""If you don't want to send notices to all channels sopel joined,
specify here the channels you want.
"""
INTERVAL_SECONDS = 30
"""Interval in seconds to check for new videos"""
###

API_URL = "http://openings.moe/api/list.php"
CURDIR = os.path.dirname(os.path.realpath(__file__))
JSONFILE = os.path.join(CURDIR, "aoupdates_data.json")


def send_notice(bot, message):
    """Send an IRC NOTICE"""
    global CHANNELS

    if not CHANNELS:
        CHANNELS = bot.channels
    for channel in CHANNELS:
        bot.notice(message, dest=channel)


def api_request():
    """Form an API request"""
    request = urllib.request.Request(API_URL)
    request.add_header("Cache-Control", "max-age=0")
    return urllib.request.urlopen(request).read().decode("utf-8")


@module.interval(INTERVAL_SECONDS)
def check_for_updates(bot):
    """Check for new videos

    If one or more videos have been found, notice them to the
    channel(s) and return the quantity of published videos.
    """
    # Do not check for new videos if the bot is not connected to any channel
    if not bot.channels:
        return

    try:
        response = api_request()
        response = json.loads(response)

        f = open(JSONFILE, "r")
        oldfile = json.load(f)
        f.close()

        if response != oldfile:
            video_count = 0
            series_count = 0
            dic = []
            series_list = []
            send_counts = False

            for item in oldfile:
                dic.append(item["file"])

            for item in response:
                # count videos and series in response
                video_count += 1
                if item["source"] not in series_list:
                    series_list.append(item["source"])
                    series_count += 1

                # search for new videos
                if not item["file"] in dic:
                    print("[aoupdates] New item found! {}".format(item["file"]))
                    send_notice(bot, "New video! {} from {} http://openings.moe/?video={}".format(
                        item["title"], item["source"], item["file"]))
                    send_counts = True
                    time.sleep(1)

            if send_counts:
                send_notice(bot, "Now serving {} videos from {} series!".format(
                    video_count, series_count))

        with open(JSONFILE, "w") as f:
            json.dump(response, f, sort_keys=True, indent=4)
    except:
        traceback.print_exc(file=sys.stdout)


def setup(bot):
    """Get the current content from the website"""
    try:
        response = api_request()
        with open(JSONFILE, "w") as f:
            json.dump(json.loads(response), f, sort_keys=True, indent=4)
    except:
        traceback.print_exc(file=sys.stdout)


def shutdown(bot):
    """Delete the json file when shutting down"""
    os.remove(JSONFILE)
