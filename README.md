# Twitter Video Bot Lambda
## Lambda which replies to video comments with the video URL, deployed via AWS Cloud Development Kit

You will need a Twitter Developer account. Apply here:

https://developer.twitter.com/en/apply-for-access

The app will search for the search string defined in utils

#### 1. Add your Twitter/AWS details
The project pulls the api keys from AWS SSM param store, add these to the same path as outlined in the
cdk-twitter-stack.ts param lookups:


Token - '/twitterlambda/accesstoken'

Access token secret - '/twitterlambda/accesstokensecret'

Consumer key - '/twitterlambda/consumerkey'

Consumer key secret - '/twitterlambda/consumersecretkey'

#### 2. Export your aws profile

```sh
$ export AWS_PROFILE=<aws profile>
```

#### 3. Install Requirements/dependencies
The requirements need to be packaged within the project for AWS lambda. The following installs the packages in a 
dependencies directory, and installs the node packages for CDK:
```sh
$ pip install -r src/requirements.txt -t src/dependencies
$ npm install
```

#### 4. Compile typescript
```sh
$  npm run watch
```

#### 3. Generate Cloudformation Template for stack:

```sh
$  cdk synth
```
#### 3. Deploy the stack:

```sh
$  cdk deploy
```

#### 5. Destroy the stack:

```sh
$  cdk destroy
```
