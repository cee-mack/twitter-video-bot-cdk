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
    if event:
        username: str = event['username'].lower()
        tweet_id: int = event['tweet_id']
        video_link: str = event['video_link']

        write_tweet_to_db(username, tweet_id, video_link)


def write_tweet_to_db(username: str, tweet_id: int, video_link: str):
    user_document: dict = get_document(username)
    expiration_date = int(time.time()) + (int(expiration_days) * 86400)

    if 'Item' in user_document:
        number_of_existing_tweets: int = len(user_document['Item']['tweet'])
        update_user_document(username, tweet_id, video_link, number_of_existing_tweets, expiration_date)
    else:
        put_new_user_document(username, tweet_id, video_link, expiration_date)


def get_document(username: str):
    document: dict = table.get_item(
        Key={
            'username': username
        })

    return document


def update_user_document(username: str, tweet_id: int, video_link: str, number_of_existing_tweets: int, expiration_date: int):
    """
    If the document already has 5 tweets saved,
    this will first remove the oldest of them
    before inserting the new record.
    """
    if number_of_existing_tweets >= 5:
        update = table.update_item(
            Key={
                'username': username
            },
            UpdateExpression='REMOVE tweet[0]',
            ReturnValues="UPDATED_NEW"
            )

    update = table.update_item(
        Key={
            'username': username
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

    return update


def put_new_user_document(username: str, tweet_id: int, video_link: str, expiration_date: int):
    put_id = table.put_item(
        Item={
            'username': username,
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
