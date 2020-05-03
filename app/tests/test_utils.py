from ..src import utils


def test_construct_message():
    message = '@AccountName Beep beep boop I am a bot! http://video-link'
    assert utils.construct_message('AccountName', 'http://video-link') == message
