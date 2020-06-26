import events = require('@aws-cdk/aws-events');
import targets = require('@aws-cdk/aws-events-targets');
import lambda = require('@aws-cdk/aws-lambda');
import { AwsIntegration, Cors, RestApi } from '@aws-cdk/aws-apigateway';
import ssm = require('@aws-cdk/aws-ssm');
import iam = require('@aws-cdk/aws-iam');
import dynamodb = require('@aws-cdk/aws-dynamodb');
import path = require('path');
import * as cdk from '@aws-cdk/core';
import {RemovalPolicy} from '@aws-cdk/core';
import {PolicyStatement} from "@aws-cdk/aws-iam";

export class CdkTwitterStack extends cdk.Stack {
    constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        const accountId = cdk.Stack.of(this).account;
        const region = cdk.Stack.of(this).region;
        const twitterLambdaName = 'cdk-twitter-lambda';
        const dynamoLambdaName = 'cdk-dynamo-lambda';
        const dynamoTableName = 'cdk-twitter-dynamo';
        const apiName = 'TwitterAppApi';
        const pythonPath = '/var/task/dependencies:/var/runtime';

        const accessToken = ssm.StringParameter.fromStringParameterAttributes(this, 'accessToken', {
            parameterName: '/twitterlambda/accesstoken',
        }).stringValue;

        const accessTokenSecret = ssm.StringParameter.fromStringParameterAttributes(this, 'accessTokenSecret', {
            parameterName: '/twitterlambda/accesstokensecret',
        }).stringValue;

        const consumerKey = ssm.StringParameter.fromStringParameterAttributes(this, 'consumerKey', {
            parameterName: '/twitterlambda/consumerkey',
        }).stringValue;

        const consumerSecret = ssm.StringParameter.fromStringParameterAttributes(this, 'consumerSecret', {
            parameterName: '/twitterlambda/consumersecretkey',
        }).stringValue;

        const searchString = ssm.StringParameter.fromStringParameterAttributes(this, 'searchString', {
            parameterName: '/twitterlambda/searchstring',
        }).stringValue;

        const twitterAccountName = ssm.StringParameter.fromStringParameterAttributes(this, 'twitterAccountName', {
            parameterName: '/twitterlambda/twitteraccountname',
        }).stringValue;

        const expiration = ssm.StringParameter.fromStringParameterAttributes(this, 'expiration', {
            parameterName: '/twitterlambda/expiration',
        }).stringValue;


        const twitterLambdaRole = new iam.Role(this, 'twitterLambdaRole', {
            assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com')
        });

        const apiRole = new iam.Role(this, 'apiRole', {
            assumedBy: new iam.ServicePrincipal('apigateway.amazonaws.com')
        });

        const dynamoLambdaRole = new iam.Role(this, 'dynamoLambdaRole', {
            assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com')
        });

        twitterLambdaRole.addToPolicy(new PolicyStatement({
            resources: ['*'],
            actions: [
                'logs:CreateLogGroup',
                'logs:CreateLogStream',
                'logs:PutLogEvents']
        }));

        twitterLambdaRole.addToPolicy(new PolicyStatement({
            resources: [`arn:aws:lambda:${region}:${accountId}:function:${dynamoLambdaName}`],
            actions: [
                'lambda:InvokeFunction']
        }));

        dynamoLambdaRole.addToPolicy(new PolicyStatement({
            resources: [`arn:aws:dynamodb:${region}:${accountId}:table/${dynamoTableName}`],
            actions: [
                'dynamodb:PutItem',
                'dynamodb:UpdateItem',
                'dynamodb:DeleteItem',
                'dynamodb:GetItem']
        }));

        dynamoLambdaRole.addToPolicy(new PolicyStatement({
            resources: ['*'],
            actions: [
                'logs:CreateLogGroup',
                'logs:CreateLogStream',
                'logs:PutLogEvents']
        }));

        apiRole.addToPolicy(new PolicyStatement({
            resources: [`arn:aws:dynamodb:${region}:${accountId}:table/${dynamoTableName}`],
            actions: [
                'dynamodb:GetItem']
        }));

        const twitterLambdaFunction = new lambda.Function(this, twitterLambdaName, {
            functionName: twitterLambdaName,
            code: lambda.Code.fromAsset(path.join(__dirname, '../app/src')),
            role: twitterLambdaRole,
            handler: 'twitter_lambda.main.handler',
            runtime: lambda.Runtime.PYTHON_3_8,
            timeout: cdk.Duration.seconds(10),
            environment: {
                'CONSUMERKEY': consumerKey,
                'CONSUMERSECRET': consumerSecret,
                'ACCESSTOKEN': accessToken,
                'ACCESSTOKENSECRET': accessTokenSecret,
                'SEARCHSTRING': searchString,
                'REGION': region,
                'TWITTERACCOUNTNAME': twitterAccountName,
                'ACCOUNTID': accountId,
                'PYTHONPATH': pythonPath
            }
        });

        const dynamoLambdaFunction = new lambda.Function(this, dynamoLambdaName, {
            functionName: dynamoLambdaName,
            code: lambda.Code.fromAsset(path.join(__dirname, '../app/src')),
            role: dynamoLambdaRole,
            handler: 'dynamo_lambda.main.handler',
            runtime: lambda.Runtime.PYTHON_3_8,
            timeout: cdk.Duration.seconds(10),
            environment: {
                'REGION': region,
                'EXPIRATION': expiration,
                'PYTHONPATH': pythonPath
            }
        });

        const twitterLambdaRule = new events.Rule(this, 'twitterLambdaRule', {
            schedule: events.Schedule.expression('cron(0/1 * * * ? *)')
        });

        twitterLambdaRule.addTarget(new targets.LambdaFunction(twitterLambdaFunction));

        new dynamodb.Table(this, dynamoTableName, {
            tableName: dynamoTableName,
            removalPolicy: RemovalPolicy.DESTROY,
            partitionKey: {name: 'username', type: dynamodb.AttributeType.STRING},
            billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
            timeToLiveAttribute: 'expiry'
        });

        const api = new RestApi(this, apiName, {
            defaultCorsPreflightOptions: {
                allowOrigins: Cors.ALL_ORIGINS,
            },
            restApiName: apiName,
        });

        const allResources = api.root.addResource(apiName.toLocaleLowerCase());

        const oneResource = allResources.addResource('{id}');

        const errorResponses = [
            {
                selectionPattern: '400',
                statusCode: '400',
                responseTemplates: {
                    'application/json': `{
                        "error": "Bad Input"
                    }`,
            },
            },
            {
                selectionPattern: '5\\d{2}',
                statusCode: '500',
                responseTemplates: {
                    'application/json': `{
                    "error": "Internal Service Error"
                    }`,
                },
            },
        ];

        const integrationResponses = [
            {
                statusCode: '200',
            },
            ...errorResponses,
        ];

        const getIntegration = new AwsIntegration({
            action: 'GetItem',
            options: {
                credentialsRole: apiRole,
                integrationResponses,
                requestTemplates: {
                    'application/json': `{
                        "Key": {
                            "username": {
                            "S": "$method.request.path.id"
                        }
                    },
                    "TableName": "${dynamoTableName}"
                }`,
                },
            },
            service: 'dynamodb',
        });

        const methodOptions = { methodResponses: [{ statusCode: '200' }, { statusCode: '400' }, { statusCode: '500' }] };

        oneResource.addMethod('GET', getIntegration, methodOptions);
    }
}
