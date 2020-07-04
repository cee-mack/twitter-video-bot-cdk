import boto3
import os
import logging
import json


logger = logging.getLogger()
logger.setLevel(logging.INFO)
region = os.getenv('REGION')

session = boto3.session.Session()
dynamodb = session.resource('dynamodb', region)
table = dynamodb.Table('cdk-twitter-dynamo')

def handler(event, context):
    if event:
        username = event['pathParameters']['item']
        document = queryDynamo(username)

        if 'Item' in document:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "document": document
                })
            }
        else:
            logger.info(f'No document found in Dynamo for user: {username}')
            return {
                "statusCode": 404,
                "body": json.dumps({
                    "error": "Not found"
                })
            }

def queryDynamo(username):
    document = table.get_item(
        Key={
            'username': username
        })

    return str(document)