import tweepy
import boto3
import os
import logging
import json


logger = logging.getLogger()
logger.setLevel(logging.INFO)

consumer_key = os.getenv('CONSUMERKEY')
consumer_secret = os.getenv('CONSUMERSECRET')
access_token = os.getenv('ACCESSTOKEN')
access_token_secret = os.getenv('ACCESSTOKENSECRET')
search_string = os.getenv('SEARCHSTRING')
twitter_account_name = os.getenv('TWITTERACCOUNTNAME')
account_id = os.getenv('ACCOUNTID')
region = os.getenv('REGION')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

client = boto3.client('lambda')

def handler(event, context):
    reply_to_statuses()


class Tweet:
    def __init__(self, result):
        self.result = result
        self.video_link = None
        self.tweet_id = self.result._json['id']
        self.parent_tweet_id = self.result._json['in_reply_to_status_id']
        self.user_screen_name = self.result._json['user']['screen_name']

    def set_video_link(self, link):
        self.video_link = link

    def asdict(self):
        return {
            "tweet_id": self.tweet_id,
            "username": self.user_screen_name,
            "video_link": self.video_link
        }

def reply_to_statuses():

    get_latest_id = api.get_user(twitter_account_name)
    latest_id = get_latest_id._json['status']['id'] - 1

    search = api.search(search_string, tweet_mode='extended', since_id=latest_id)

    logger.info(f'Search {search}')

    if search:
        for result in search:
            tweet = Tweet(result)
            parent_tweet_data = api.get_status(tweet.parent_tweet_id, tweet_mode='extended')
            tweet.set_video_link(return_highest_bitrate(parent_tweet_data._json))
            api.update_status(construct_message(tweet.user_screen_name, tweet.video_link), tweet.tweet_id)

            if tweet.video_link:
                invoke_dynamo_lambda(tweet.asdict())
            else:
                logger.info(f'No video was found under comment for tweet ID {tweet.tweet_id}')

    else:
        logger.info('Search returned no results')


def construct_message(user_screen_name, video_link):
    if video_link:
        return f'@{user_screen_name} Beep beep boop I am a bot! {video_link}'
    else:
        return f'@{user_screen_name} Sorry! No video was found :('


def return_highest_bitrate(parent_tweet_data):
    def get_video_bitrate(video):
        return video['bitrate']

    try:
        parent_video_url = parent_tweet_data['extended_entities']['media'][0]['video_info']['variants']
        mp4_videos = [video for video in parent_video_url if video['content_type'] == 'video/mp4']
        highest_bitrate_video = max(mp4_videos, key=get_video_bitrate)
        return highest_bitrate_video['url']

    except KeyError:
        return None

def invoke_dynamo_lambda(tweet_data):
    response = client.invoke(
    FunctionName=f'arn:aws:lambda:{region}:{account_id}:function:cdk-dynamo-lambda',
    InvocationType='RequestResponse',
    LogType='None',
    Payload=json.dumps(tweet_data),
    )

    logger.info(f'Invoked dynamo lambda with response: {response}')