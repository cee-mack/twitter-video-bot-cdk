import boto3
import time
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

region = os.environ['REGION']

session = boto3.session.Session()
dynamodb = session.resource('dynamodb', region)
table = dynamodb.Table('cdk-twitter-dynamo')


def write_last_id(id):
    last_id = get_latest_id()

    put_id = table.put_item(
        Item={
            'id': str(id),
            'timestamp': int(time.time())
        }
    )
    if put_id['ResponseMetadata']['HTTPStatusCode'] == 200:
        logger.info(f'Successfully put id {id} into dynamoDb')
        delete_id = delete_last_item(last_id)
        if delete_id['ResponseMetadata']['HTTPStatusCode'] == 200:
            logger.info(f'Successfully deleted id {last_id} from dynamoDb')
        else:
            logger.error(f'Error deleting id {last_id} from dynamoDb')
    else:
        logger.error(f'Could not put latest id {id} into dynamoDb, previous ID remains')


def get_latest_id():
    data = table.scan()

    return data['Items'][0]['id']


def delete_last_item(id):
    delete = table.delete_item(TableName='cdk-twitter-dynamo',
                               Key={
                                   'id': id
                               }
                               )
    return delete
