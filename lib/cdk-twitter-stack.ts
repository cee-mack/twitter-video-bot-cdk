import { Rule, Schedule } from '@aws-cdk/aws-events';
import { LambdaFunction as LambdaFunctionTarget } from '@aws-cdk/aws-events-targets';
import { Code, Runtime, Function as LambdaFunction } from '@aws-cdk/aws-lambda';
import { AwsIntegration, Cors, RestApi } from '@aws-cdk/aws-apigateway';
import { StringParameter } from '@aws-cdk/aws-ssm';
import { Role, ServicePrincipal } from  '@aws-cdk/aws-iam';
import { Table, AttributeType, BillingMode } from '@aws-cdk/aws-dynamodb';
import { RemovalPolicy } from '@aws-cdk/core';
import { PolicyStatement } from "@aws-cdk/aws-iam";
import * as cdk from '@aws-cdk/core';

import path = require('path');

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

        const accessToken = StringParameter.fromStringParameterAttributes(this, 'accessToken', {
            parameterName: '/twitterlambda/accesstoken',
        }).stringValue;

        const accessTokenSecret = StringParameter.fromStringParameterAttributes(this, 'accessTokenSecret', {
            parameterName: '/twitterlambda/accesstokensecret',
        }).stringValue;

        const consumerKey = StringParameter.fromStringParameterAttributes(this, 'consumerKey', {
            parameterName: '/twitterlambda/consumerkey',
        }).stringValue;

        const consumerSecret = StringParameter.fromStringParameterAttributes(this, 'consumerSecret', {
            parameterName: '/twitterlambda/consumersecretkey',
        }).stringValue;

        const searchString = StringParameter.fromStringParameterAttributes(this, 'searchString', {
            parameterName: '/twitterlambda/searchstring',
        }).stringValue;

        const twitterAccountName = StringParameter.fromStringParameterAttributes(this, 'twitterAccountName', {
            parameterName: '/twitterlambda/twitteraccountname',
        }).stringValue;

        const expiration = StringParameter.fromStringParameterAttributes(this, 'expiration', {
            parameterName: '/twitterlambda/expiration',
        }).stringValue;


        const twitterLambdaRole = new Role(this, 'twitterLambdaRole', {
            assumedBy: new ServicePrincipal('lambda.amazonaws.com')
        });

        const apiRole = new Role(this, 'apiRole', {
            assumedBy: new ServicePrincipal('apigateway.amazonaws.com')
        });

        const dynamoLambdaRole = new Role(this, 'dynamoLambdaRole', {
            assumedBy: new ServicePrincipal('lambda.amazonaws.com')
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

        const twitterLambdaFunction = new LambdaFunction(this, twitterLambdaName, {
            functionName: twitterLambdaName,
            code: Code.fromAsset(path.join(__dirname, '../lambdas/src')),
            role: twitterLambdaRole,
            handler: 'twitter_lambda.main.handler',
            runtime: Runtime.PYTHON_3_8,
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

        const dynamoLambdaFunction = new LambdaFunction(this, dynamoLambdaName, {
            functionName: dynamoLambdaName,
            code: Code.fromAsset(path.join(__dirname, '../lambdas/src')),
            role: dynamoLambdaRole,
            handler: 'dynamo_lambda.main.handler',
            runtime: Runtime.PYTHON_3_8,
            timeout: cdk.Duration.seconds(10),
            environment: {
                'REGION': region,
                'EXPIRATION': expiration,
                'PYTHONPATH': pythonPath
            }
        });

        const twitterLambdaRule = new Rule(this, 'twitterLambdaRule', {
            schedule: Schedule.expression('cron(0/1 * * * ? *)')
        });

        twitterLambdaRule.addTarget(new LambdaFunctionTarget(twitterLambdaFunction));

        new Table(this, dynamoTableName, {
            tableName: dynamoTableName,
            removalPolicy: RemovalPolicy.DESTROY,
            partitionKey: {name: 'username', type: AttributeType.STRING},
            billingMode: BillingMode.PAY_PER_REQUEST,
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
