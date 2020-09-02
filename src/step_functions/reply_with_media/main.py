import tweepy
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

consumer_key = os.getenv('CONSUMERKEY')
consumer_secret = os.getenv('CONSUMERSECRET')
access_token = os.getenv('ACCESSTOKEN')
access_token_secret = os.getenv('ACCESSTOKENSECRET')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


def handler(event: dict, context):

    tweet_id = event["tweet_id"]
    user_screen_name = event["user_screen_name"]
    video_link = event["video_link"]

    reply = f'@{user_screen_name} Beep beep boop I am a bot! {video_link}'
    api.update_status(reply, tweet_id)

    payload = {
        "tweet_id": tweet_id,
        "user_screen_name": user_screen_name,
        "video_link": video_link
    }

    return payload
