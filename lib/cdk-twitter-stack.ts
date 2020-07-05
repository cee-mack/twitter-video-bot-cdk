import { Rule, Schedule } from '@aws-cdk/aws-events';
import { LambdaFunction as LambdaFunctionTarget } from '@aws-cdk/aws-events-targets';
import { Code, Runtime, Function as LambdaFunction } from '@aws-cdk/aws-lambda';
import { LambdaRestApi } from '@aws-cdk/aws-apigateway';
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
        const uiLambdaName = 'cdk-ui-lambda';
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

        const dynamoLambdaRole = new Role(this, 'dynamoLambdaRole', {
            assumedBy: new ServicePrincipal('lambda.amazonaws.com')
        });

        const uiLambdaRole = new Role(this, 'uiLambdaRole', {
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

        uiLambdaRole.addToPolicy(new PolicyStatement({
            resources: [`arn:aws:dynamodb:${region}:${accountId}:table/${dynamoTableName}`],
            actions: [
                'dynamodb:GetItem']
        }));

        dynamoLambdaRole.addToPolicy(new PolicyStatement({
            resources: ['*'],
            actions: [
                'logs:CreateLogGroup',
                'logs:CreateLogStream',
                'logs:PutLogEvents']
        }));

        uiLambdaRole.addToPolicy(new PolicyStatement({
            resources: ['*'],
            actions: [
                'logs:CreateLogGroup',
                'logs:CreateLogStream',
                'logs:PutLogEvents']
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


        const uiLambdaFunction = new LambdaFunction(this, uiLambdaName, {
            functionName: uiLambdaName,
            code: Code.fromAsset(path.join(__dirname, '../lambdas/src')),
            role: uiLambdaRole,
            handler: 'ui_lambda.main.handler',
            runtime: Runtime.PYTHON_3_8,
            timeout: cdk.Duration.seconds(10),
            environment: {
                'REGION': region,
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

        const api = new LambdaRestApi(this, 'uiApi', {
            handler: uiLambdaFunction,
            proxy: false,
        });

        const items = api.root.addResource('items');
            items.addMethod('GET');

        const item = items.addResource('{item}');
            item.addMethod('GET');
    }
}
