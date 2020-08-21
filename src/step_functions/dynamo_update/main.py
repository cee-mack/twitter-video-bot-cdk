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

    user_document = table.get_item(
        Key={
            'username': user_screen_name
        })

    number_of_existing_tweets = len(user_document['Item']['tweet'])

    if number_of_existing_tweets >= 5:
        update = table.update_item(
            Key={
                'username': user_screen_name
            },
            UpdateExpression='REMOVE tweet[0]',
            ReturnValues="UPDATED_NEW"
            )

    update = table.update_item(
        Key={
            'username': user_screen_name
        },
        UpdateExpression="SET tweet = list_append(tweet, :i), expiry = :e",
        ExpressionAttributeValues={
            ':e': expiration_date,
            ':i': [{'id': tweet_id,
                    'url': video_link,
                    'created': int(time.time())
                    }],
        },
        ReturnValues="UPDATED_NEW"
    )
