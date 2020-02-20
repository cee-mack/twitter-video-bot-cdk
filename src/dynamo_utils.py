import boto3
import time
import os

region = os.environ['REGION']

session = boto3.session.Session()
dynamodb = session.resource('dynamodb', region)
table = dynamodb.Table('cdk-twitter-dynamo')


def write_last_id(id):
    delete_last_item()
    table.put_item(
        Item={
            'id': str(id),
            'timestamp': int(time.time())
        }
    )


def get_latest_id():
    data = table.scan()
    return data['Items'][0]['id']


def delete_last_item():
    table.delete_item(TableName='cdk-twitter-dynamo',
                      Key={
                          'id': get_latest_id()
                      }
                      )
