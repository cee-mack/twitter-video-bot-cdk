from ..src.twitter_lambda import main
import pytest
import os
import json


@pytest.fixture
def tweet_object_with_media():
    with open(os.path.abspath("lambdas/tests/resources/object_with_media.json")) as f:
        return json.loads(f.read())


@pytest.fixture
def tweet_object_without_media():
    with open(os.path.abspath("lambdas/tests/resources/object_without_media.json")) as f:
        return json.loads(f.read())


def test_construct_message():
    message = '@AccountName Beep beep boop I am a bot! http://video-link'
    assert main.construct_message('AccountName', 'http://video-link') == message


def test_return_highest_bitrate(tweet_object_with_media):
    highest_bitrate_url = 'https://video.twimg.com/ext_tw_video/eKhST407BSvI15sR.mp4'
    assert main.return_highest_bitrate(tweet_object_with_media) == highest_bitrate_url


def test_return_highest_bitrate_with_no_media(tweet_object_without_media):
    assert main.return_highest_bitrate(tweet_object_without_media) is None
