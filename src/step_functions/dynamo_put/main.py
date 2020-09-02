import boto3
import time
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

region = os.getenv('REGION')
expiration_days = os.getenv('EXPIRATION')

session = boto3.session.Session()
dynamodb = session.resource('dynamodb', region)
table = dynamodb.Table('cdk-twitter-dynamo')


def handler(event: dict, context):

    tweet_id = event["tweet_id"]
    user_screen_name = event["user_screen_name"]
    video_link = event["video_link"]
    expiration_date = int(time.time()) + (int(expiration_days) * 86400)

    put_id = table.put_item(
        Item={
            'username': user_screen_name,
            'expiry': expiration_date,
            'tweet': [
                {'id': tweet_id,
                 'url': video_link,
                 'created': int(time.time())
                 }
            ]
        }
    )
    return put_id
