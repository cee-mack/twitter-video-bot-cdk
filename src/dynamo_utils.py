import boto3
import time
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

session = boto3.session.Session()
dynamodb = session.resource('dynamodb', 'eu-west-1')
table = dynamodb.Table('play')


def write_tweet(username, tweet_id):
    user_document = get_document(username)

    if 'Item' in user_document:
        update_user_document(username, tweet_id)
    else:
        put_new_user_document(username, tweet_id)


def return_latest_tweet_id():
    latest = get_document('latest_tweet_id')
    return latest['Item']['id']


def write_latest_tweet_id(latest_tweet_id):
    update = table.update_item(
        Key={
            'username': 'latest_tweet_id'
        },
        UpdateExpression="SET id = :i",
        ExpressionAttributeValues={
            ':i': latest_tweet_id,
        },
        ReturnValues="UPDATED_NEW"
    )

    return update


def get_document(username):
    document = table.get_item(
        Key={
            'username': username
        })

    return document


def update_user_document(username, tweet_id):
    update = table.update_item(
        Key={
            'username': username
        },
        UpdateExpression="SET tweet = list_append(tweet, :i)",
        ExpressionAttributeValues={
            ':i': [{'id': tweet_id,
                    'created': int(time.time())
                    }],
        },
        ReturnValues="UPDATED_NEW"
    )

    return update


def put_new_user_document(username, tweet_id):
    put_id = table.put_item(
        Item={
            'username': username,
            'tweet': [
                {'id': tweet_id,
                 'created': int(time.time())
                 }
            ]
        }
    )
    return put_id
