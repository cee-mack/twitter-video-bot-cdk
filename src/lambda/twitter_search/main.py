import tweepy
import boto3
import os
import logging
import json

from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

consumer_key = os.getenv('CONSUMERKEY')
consumer_secret = os.getenv('CONSUMERSECRET')
access_token = os.getenv('ACCESSTOKEN')
access_token_secret = os.getenv('ACCESSTOKENSECRET')
search_string = os.getenv('SEARCHSTRING')
twitter_account_name = os.getenv('TWITTERACCOUNTNAME')
state_machine_arn = os.getenv('STATE_MACHINE_ARN')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

client = boto3.client("stepfunctions")


def handler(event: dict, context):

    main_account_tweets = api.get_user(twitter_account_name)
    latest_id = main_account_tweets._json['status']['id'] - 1

    search = api.search(search_string, tweet_mode='extended', since_id=latest_id)

    if search:
        for result in search:
            payload = {
                "tweet_id": str(result._json['id']),
                "parent_tweet_id": result._json['in_reply_to_status_id'],
                "user_screen_name": result._json['user']['screen_name']
            }
            try:
                logger.info(f"Executing Step Function", {
                "tweet_id": payload["tweet_id"]
            })
                client.start_execution(
                    stateMachineArn=state_machine_arn,
                    name=f"execution-tweet-{payload['tweet_id']}",
                    input=json.dumps(payload)
                )
            except ClientError as err:
                logger.error(err)
