#!/usr/bin/env node
import * as cdk from '@aws-cdk/core';
import { CdkTwitterStack } from '../lib/cdk-twitter-stack';

const app = new cdk.App();
new CdkTwitterStack(app, 'CdkTwitterStack', {
  env: {
    account: process.env.CDK_DEPLOY_ACCOUNT || process.env.CDK_DEFAULT_ACCOUNT || 'personal',
    region: process.env.CDK_DEPLOY_REGION || process.env.CDK_DEFAULT_REGION || 'eu-west-1'
}});
