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

def handler(event: dict, context):

    main_account_tweets: tweepy.models.User = api.get_user(twitter_account_name)
    latest_id: int = main_account_tweets._json['status']['id'] - 1

    search: tweepy.models.SearchResults = api.search(search_string, tweet_mode='extended', since_id=latest_id)
    reply_to_statuses(search)


def reply_to_statuses(search: tweepy.models.SearchResults):

    logger.info(f'Search {search}')

    if search:
        for result in search:
            tweet_id: int = result._json['id']
            parent_tweet_id: int = result._json['in_reply_to_status_id']
            user_screen_name: str = result._json['user']['screen_name']
            parent_tweet_data: tweepy.models.Status = api.get_status(parent_tweet_id, tweet_mode='extended')

            video_link = return_highest_bitrate(parent_tweet_data._json)
            api.update_status(construct_message(user_screen_name, video_link), tweet_id)

            if video_link:
                invoke_dynamo_lambda(tweet_id, user_screen_name, video_link)
            else:
                logger.info(f'No video was found under comment for tweet ID {tweet_id}')

    else:
        logger.info('Search returned no results')


def construct_message(user_screen_name: str, video_link: str):
    if video_link:
        return f'@{user_screen_name} Beep beep boop I am a bot! {video_link}'
    return f'@{user_screen_name} Sorry! No video was found :('


def return_highest_bitrate(parent_tweet_data: tweepy.models.Status):
    def get_video_bitrate(video: dict):
        return video['bitrate']

    try:
        parent_video_url: str = parent_tweet_data['extended_entities']['media'][0]['video_info']['variants']
        mp4_videos: list = [video for video in parent_video_url if video['content_type'] == 'video/mp4']
        highest_bitrate_video: dict = max(mp4_videos, key=get_video_bitrate)
        return highest_bitrate_video['url']

    except KeyError:
        return None

def invoke_dynamo_lambda(tweet_id: int, user_screen_name: str, video_link: str):
    response = client.invoke(
    FunctionName=f'arn:aws:lambda:{region}:{account_id}:function:cdk-dynamo-lambda',
    InvocationType='RequestResponse',
    LogType='None',
    Payload=json.dumps({
            "tweet_id": tweet_id,
            "username": user_screen_name,
            "video_link": video_link
        }),
    )

    logger.info(f'Invoked dynamo lambda with response: {response}')