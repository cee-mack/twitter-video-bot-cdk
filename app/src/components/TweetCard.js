import React from 'react';
import { useFetch } from '../hooks/hooks'


function TweetCard() {

  const response = useFetch('https://4er40lpzhf.execute-api.eu-west-1.amazonaws.com/prod/twitterappapi/DownloadMeBot', {});

  console.log(response)

  return (
    <div>
      {/* <h1>Your Twitter Username</h1>
      <div>
      <video width="320" height="240" controls>
        <source src={video_url} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      </div>
        <a href={tweet_link}>Original Tweet</a> */}
    </div>
  )
}


export default TweetCard;