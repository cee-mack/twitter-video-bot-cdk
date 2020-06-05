import boto3
import time
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

region = os.getenv('REGION')

session = boto3.session.Session()
dynamodb = session.resource('dynamodb', region)
table = dynamodb.Table('cdk-twitter-dynamo')


def handler(event, context):
    if event:
        username = event['username']
        tweet_id = event['tweet_id']
        video_link = event['video_link']

        write_tweet_to_db(username, tweet_id, video_link)

    print(event)

def write_tweet_to_db(username, tweet_id, video_link):
    user_document = get_document(username)

    if 'Item' in user_document:
        update_user_document(username, tweet_id, video_link)
    else:
        put_new_user_document(username, tweet_id, video_link)


def get_document(username):
    document = table.get_item(
        Key={
            'username': username
        })

    return document


def update_user_document(username, tweet_id, video_link):
    update = table.update_item(
        Key={
            'username': username
        },
        UpdateExpression="SET tweet = list_append(tweet, :i)",
        ExpressionAttributeValues={
            ':i': [{'id': tweet_id,
                    'url': video_link,
                    'created': int(time.time())
                    }],
        },
        ReturnValues="UPDATED_NEW"
    )

    return update


def put_new_user_document(username, tweet_id, video_link):
    put_id = table.put_item(
        Item={
            'username': username,
            'tweet': [
                {'id': tweet_id,
                'url': video_link,
                'created': int(time.time())
                }
            ]
        }
    )
    return put_id
