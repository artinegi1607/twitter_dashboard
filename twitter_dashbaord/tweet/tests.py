import json

from mock import patch
from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.core.urlresolvers import reverse

from tweet.tasks import CustomStreamListener
from tweet.tweets import get_or_create_tweet
from tweet.models import Tweet

MOCK_DATA = {
    'user': 'test-user',
    'email': 'testuser@example.com',
    'password': 'test-user',
    'test_id': '12345',
    'screen_name1': 'test1',
    'sample_tweet': 'test tweet',
    'test_id2': '45356',
    'screen_name2': 'test2',
    'stream_tweet': 'test stream',
    'created_at': 'Mon Apr 30 14:53:06 +0000 2018',  # twitter date format
    'profile_image': '',
    'count': 200
}


class PatchedOAuthHandler(object):
    """
     This class mock OAuthHandler class of tweepy library.
    """

    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

    def set_access_token(self, *args):
        pass


class PatchedAPI(object):
    """
     This class mock API class of tweepy library.
    """
    def __init__(self, auth):
        self.auth = auth

    def user_timeline(*args, **kwargs):
        screen_name = kwargs['screen_name']
        tweet = TwitterMockResponse()
        tweet.set_tweet_val(id_str=MOCK_DATA['test_id'],
                            screen_name=screen_name,
                            created_at=datetime.now(),
                            text=MOCK_DATA['sample_tweet'],
                            profile_image=MOCK_DATA["profile_image"])

        # save tweets into database
        get_or_create_tweet(tweet)
        return [tweet]

    def get_user(self, *args):
        return MOCK_DATA['test_id']


class StreamPatchAPI(object):
    """
    This custom class mocks Stream class from tweepy.
    """

    def __init__(self, user_id):
        self.user_id = user_id

    def filter(self, follow=[]):
        if not follow:
            return None

        tweet = TwitterMockResponse()
        tweet.set_tweet_val(id_str=MOCK_DATA['test_id2'],
                            screen_name=MOCK_DATA['screen_name2'],
                            created_at=MOCK_DATA['created_at'],
                            text=MOCK_DATA['stream_tweet'],
                            profile_image=MOCK_DATA["profile_image"])

        data = self.format_data(tweet)

        # calling its corresponding listener and storing data into the database
        listener = CustomStreamListener()
        listener.on_data(data)
        return {'data': 'data'}

    def format_data(self, data):
        data = {
            "id_str": data.id_str,
            "user": {
                "screen_name": data.user.screen_name,
                "profile_image_url": data.user.profile_image_url
            },
            "created_at": data.created_at,
            "text": data.text
        }
        return json.dumps(data)


class TwitterMockResponse:
    """-
    This class mock twitter api response for stream_tweets.
    """
    def __init__(self):
        self.user = User.objects.get_or_create(email=MOCK_DATA['email'])[0]
        self.resp = {}

    def set_tweet_val(self, id_str, screen_name, created_at, text,
                      profile_image):
        self.id_str = id_str
        self.user.screen_name = screen_name
        self.text = text
        self.user.profile_image_url = profile_image
        self.created_at = created_at
        self.resp.get('error', 'User not valid')


class GetTweetTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username=MOCK_DATA['user'],
                                             email=MOCK_DATA['email'],
                                             password=MOCK_DATA['password'])
        self.client.login(
            username=MOCK_DATA['user'],
            password=MOCK_DATA['password']
        )
        patcher_api = patch(
            'tweet.tweets.API',
            return_value=PatchedAPI
        )
        stream_patcher = patch(
            'tweet.tasks.Stream',
            return_value=StreamPatchAPI
        )

        task_api_patcher = patch(
            'tweet.tasks.API',
            return_value=PatchedAPI
        )

        oauth_task_patcher = patch(
            'tweet.tasks.OAuthHandler',
            return_value=PatchedOAuthHandler
        )

        patcher_oauth = patch(
            'tweet.tweets.OAuthHandler',
            return_value=PatchedOAuthHandler
        )

        patcher_api.start()
        stream_patcher.start()
        task_api_patcher.start()
        oauth_task_patcher.start()
        patcher_oauth.start()

        self.addCleanup(oauth_task_patcher.stop)
        self.addCleanup(patcher_api.stop)
        self.addCleanup(stream_patcher.stop)
        self.addCleanup(task_api_patcher.stop)
        self.addCleanup(patcher_oauth.stop)

    def test_get_tweets_response(self):
        api = PatchedAPI('auth')
        tweets = api.user_timeline(
            screen_name=MOCK_DATA['user'],
            count=MOCK_DATA['count'])
        for tweet in tweets:
            self.assertIsInstance(tweet.id_str, str)
            self.assertIsInstance(tweet.text, str)
            self.assertIsInstance(tweet.user.screen_name, str)
            self.assertIsInstance(tweet.created_at, datetime)
            self.assertIsInstance(tweet.user.profile_image_url, str)
        self.assertEqual(int(self.client.session['_auth_user_id']),
                         self.user.pk)

    def test_tweet_list(self):
        url = reverse('tweet:index')
        resp = self.client.get(url, {
            'username': MOCK_DATA['user']
        }, format=None)
        self.assertEqual(resp.status_code, 200)

    def test_data_response(self):
        url = reverse('tweet:stream')
        resp = self.client.get(url, {
            'username': MOCK_DATA['user']
        }, format=None)
        self.assertEqual(resp.status_code, 200)

    def test_data_for_live(self):
        url = reverse('tweet:stream')
        resp = self.client.get(url, {
            'username': MOCK_DATA['user'],
            'filter': 'live'
        }, format=None)

        self.assertEqual(resp.status_code, 200)
        self.assertLessEqual(len(json.loads(resp.content)), 20)

    def test_data_for_history(self):
        url = reverse('tweet:stream')
        resp = self.client.get(url, {
            'username': MOCK_DATA['user'],
            'filter': 'history'
        }, format=None)
        self.assertEqual(resp.status_code, 200)

    def test_stream_tweets_in_db(self):
        api = StreamPatchAPI(MOCK_DATA['test_id2'])
        api.filter(follow=[MOCK_DATA['test_id2']])
        self.assertIsInstance(
            Tweet.objects.get(tweet_id=MOCK_DATA['test_id2']),
            Tweet)
