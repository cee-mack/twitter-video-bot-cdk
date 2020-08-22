import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

region = os.getenv('REGION')

session = boto3.session.Session()
dynamodb = session.resource('dynamodb', region)
table = dynamodb.Table('cdk-twitter-dynamo')


def handler(event: dict, context):

    tweet_id = event["tweet_id"]
    user_screen_name = event["user_screen_name"]
    video_link = event['video_link']
    user_exists = 0

    user_document = table.get_item(
        Key={
            'username': user_screen_name
        })
        
    if 'Item' in user_document:
        user_exists = 1

    payload = {
        "tweet_id": tweet_id,
        "user_screen_name": user_screen_name,
        "video_link": video_link,
        "user_exists": user_exists
    }

    return payload
