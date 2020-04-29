# Twitter Video Bot Lambda
## Lambda which replies to video comments with the video URL, deployed via AWS Cloud Development Kit

You will need a Twitter Developer account. Apply here:

https://developer.twitter.com/en/apply-for-access

The app will search for the string set in param store below.

#### 1. Set up parameters in SSM param store (api keys and search string):

Search String - '/twitterlambda/searchstring'

Token - '/twitterlambda/accesstoken'

Access token secret - '/twitterlambda/accesstokensecret'

Consumer key - '/twitterlambda/consumerkey'

Consumer key secret - '/twitterlambda/consumersecretkey'

#### 2. Export your aws profile:

```sh
$ export AWS_PROFILE=<aws profile>
```

#### 3. Install Requirements/dependencies:
The requirements need to be packaged within the project for AWS lambda. The following installs the packages in a 
dependencies directory, and installs the node packages for CDK:
```sh
$ pip install -r app/requirements/base.txt -t app/src/dependencies
$ npm install
```

#### 4. Compile typescript during development:
```sh
$  npm run watch
```

#### 5. Generate Cloudformation Template for stack:

```sh
$  cdk synth
```
#### 6. Deploy the stack:

```sh
$  cdk deploy
```

#### 7. Destroy the stack:

```sh
$  cdk destroy
```
