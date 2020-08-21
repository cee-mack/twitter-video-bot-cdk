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
    parent_tweet_id = event["parent_tweet_id"]
    user_screen_name = event["user_screen_name"]

    parent_tweet_data: tweepy.models.Status = api.get_status(parent_tweet_id, tweet_mode='extended')

    video_link = return_highest_bitrate(parent_tweet_data)

    payload = {
        "tweet_id": tweet_id,
        "user_screen_name": user_screen_name,
        "video_link": video_link
    }

    return payload

def return_highest_bitrate(parent_tweet_data: tweepy.models.Status):
    """
    'media_links' is an array of dicts. The 'max' function
    beneath returns the entire dict that has the highest bitrate, if
    the content type == 'video/mp4'.
    I then query the ['url'] of the dict thats returned, and return it.
    """
    try:
        media_links: list = parent_tweet_data['extended_entities']['media'][0]['video_info']['variants']
        return max(media_links, key=lambda n:n.get("bitrate", 0) if n.get('content_type') == 'video/mp4' else False)['url']

    except KeyError:
        return None