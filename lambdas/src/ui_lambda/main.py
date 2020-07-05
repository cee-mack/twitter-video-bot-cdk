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
        documentBody = json.dumps({"document": document})
        statuscode = 200

        if 'Item' not in document:
            logger.info(f'No document found in Dynamo for user: {username}')
            statuscode = 404
            documentBody = json.dumps({"error": "No document found for given user"})

        responseBody = {
                "statusCode": statuscode,
                "body": documentBody
        }

        return responseBody

def queryDynamo(username):
    document = table.get_item(
        Key={
            'username': username
        })

    return str(document)