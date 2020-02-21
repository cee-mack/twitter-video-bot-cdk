import tweepy
import os
from dynamo_utils import *


consumer_key = os.environ['CONSUMERKEY']
consumer_secret = os.environ['CONSUMERSECRET']
access_token = os.environ['ACCESSTOKEN']
access_token_secret = os.environ['ACCESSTOKENSECRET']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

search_string = '#thisyinhere'


def reply_to_statuses():

    tweet_ids = []
    latest_id = int(get_latest_id())

    search = api.search(search_string, tweet_mode='extended', since_id=latest_id)

    if search != []:

        for result in search:
            tweet_id = result._json['id']
            parent_tweet_id = result._json['in_reply_to_status_id']
            user_screen_name = result._json['user']['screen_name']
            username = result._json['user']['name']

            tweet_ids.append(tweet_id)

            video_link = return_highest_bitrate(parent_tweet_id)
            api.update_status(construct_message(user_screen_name, username, video_link), tweet_id)

        tweet_ids.sort(reverse=True)
        write_last_id(tweet_ids[0])

    else:
        print('Search was null')


def construct_message(user_screen_name, username, highest_quality_video):
    return '@{} Here ye go {}! {}'.format(
        user_screen_name, username, highest_quality_video
    )


def return_highest_bitrate(parent_tweet_id):

    def get_video_bitrate(video):
        return video['bitrate']

    parent_tweet_data = api.get_status(parent_tweet_id, tweet_mode='extended')
    parent_video_url = parent_tweet_data._json['extended_entities']['media'][0]['video_info']['variants']

    mp4_videos = [video for video in parent_video_url if video['content_type'] == 'video/mp4']
    highest_bitrate_video = max(mp4_videos, key=get_video_bitrate)
    return highest_bitrate_video['url']
