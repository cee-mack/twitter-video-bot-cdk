import boto3
import os
import logging
import simplejson


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
        documentBody = simplejson.dumps({"document": document})
        statuscode = 200

        if 'Item' not in document:
            logger.info(f'No document found in Dynamo for user: {username}')
            statuscode = 404
            documentBody = simplejson.dumps({"error": "No document found for given user"})

        responseBody = {
                "statusCode": statuscode,
                "body": documentBody,
                "headers": {
                    "Access-Control-Allow-Headers" : "Content-Type",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET"
                }
        }

        return responseBody

def queryDynamo(username):
    document = table.get_item(
        Key={
            'username': username
        })

    return document