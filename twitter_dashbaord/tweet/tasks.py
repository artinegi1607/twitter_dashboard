from datetime import datetime
import logging
import json

from twitter_dashbaord.celery import app
from tweepy.streaming import StreamListener
from tweepy import API, OAuthHandler, Stream

from django.conf import settings
from tweet import models


class CustomStreamListener(StreamListener):
    """
    Custom listener, responsible for receiving data and store tweet into
    database
    """
    def on_data(self, data):
        data = json.loads(data)
        tweet_obj, created = models.Tweet.objects.get_or_create(
            tweet_id=data['id_str'])
        if created:
            tweet_obj.username = data['user']['screen_name']
            tweet_obj.text = data['text']
            tweet_obj.tweet_on = self.format_date(data['created_at'])
            tweet_obj.image = data['user']['profile_image_url']
            if data.get('retweeted_status', ''):
                tweet_obj.retweeted_user = \
                    data['retweeted_status']['user']['screen_name']
                tweet_obj.retweeted_user_image = \
                    data['retweeted_status']['user']['profile_image_url']
            tweet_obj.save()

        return True

    def on_error(self, status):
        logging.error(status)

    def format_date(self, _date):
        return datetime.strptime(_date, '%a %b %d %H:%M:%S +0000 %Y')


@app.task(name='stream_tweets')
def stream_tweets(username):
    """
    A background task that will open a connection and starts streaming for
    given user
    :param username: a twitter handle
    """
    consumer_key = settings.CONSUMER_KEY
    consumer_secret = settings.CONSUMER_SECRET
    access_token = settings.ACCESS_TOKEN
    access_token_secret = settings.ACCESS_SECRET

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth)

    listener = CustomStreamListener()
    socket_stream = Stream(auth=api.auth, listener=listener)
    logging.info('stream_tweets task started....')
    user = api.get_user(screen_name=username)

    if user:
        # opens a socket connection
        socket_stream.filter(follow=[user.id_str])
