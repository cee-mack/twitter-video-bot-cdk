# Twitter Video Bot
## Bot which replies to video comments with the video source URL

The bot runs via AWS step functions, and is deployed via CDK.
The Twitter Username of the requestor and video url are stored in DynamoDB with a configurable expiration date.
An API gateway endpoint is created to allow queries against the DynamoDB table. The endpoint url is returned once the stack is created. Make a GET request to:

https://{endpoint-url}/prod/items/{twitter-username}

Flow of the step function lambdas:

![step function flow](https://github.com/CrgMkz/twitter-video-bot-cdk/blob/master/step_function_flow.png?raw=true)

#### Prerequisites:
You will need a Twitter Developer account. Apply here:
https://developer.twitter.com/en/apply-for-access

You need CDK (TypeScript):
https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html

#### Set up parameters in SSM param store:

Set the following parameters in AWS SSM Param Store.
The bot will search twitter and reply to any comments that contain the search string defined below.

| Parameter  | Path  |
|---|---|
| Search String  | /twitterlambda/searchstring  |
| API Token  | /twitterlambda/accesstoken  |
| Access token secret  | /twitterlambda/accesstokensecret  |
| Consumer key  | /twitterlambda/consumerkey  |
| Consumer key secret  | /twitterlambda/consumersecretkey  |
| Twitter profile account name  | /twitterlambda/twitteraccountname  |
| Expiration in days  | /twitterlambda/expiration  |


#### Write a tweet

The app uses the last tweet ID of your account to search for new tweets, so you'll need an initial tweet to start with (any will do).

Using the account that you set in /twitterlambda/twitteraccountname, tweet any status/comment.

#### Export your aws profile:

```sh
$ export AWS_PROFILE=<aws profile>
```

#### Install Requirements/dependencies:
The requirements need to be packaged within the project for AWS lambda. The following installs the packages in a
dependencies directory, and installs the node packages for CDK:
```sh
$ pip install -r src/requirements/base.txt -t src/lambda/dependencies
$ pip install -r src/requirements/base.txt -t src/step_functions/dependencies
$ npm install
```

#### 5. Compile typescript during development:
```sh
$  npm run watch
```

#### 6. Generate Cloudformation Template for stack:

```sh
$  cdk synth
```
#### 7. Deploy the stack:

```sh
$  cdk deploy
```

#### 8. Destroy the stack:

```sh
$  cdk destroy
```
