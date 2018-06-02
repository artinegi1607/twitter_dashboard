import logging

from tweepy import API, OAuthHandler
import tweepy

from django.conf import settings
from tweet import models


def get_tweets(username):
    """
    Function to fetch tweets from twitter.
    :param username: twitter handle whose tweets are to be fetched
    :return: In case of error, returns dictionary with error message otherwise
     None.
    :raises TweepError: If oauth fails, not able to connect to twitter api or
                        any exception related to twitter
    """
    consumer_key = settings.CONSUMER_KEY
    consumer_secret = settings.CONSUMER_SECRET
    access_key = settings.ACCESS_TOKEN
    access_secret = settings.ACCESS_SECRET
    if not username:
        logging.error("No user provided")
        return None

    try:
        # Authorization to consumer key and consumer secret
        auth = OAuthHandler(consumer_key, consumer_secret)

        # Access to user's access key and access secret
        auth.set_access_token(access_key, access_secret)

        # Calling api
        api = API(auth)

    except tweepy.TweepError as msg:
        logging.error(msg)

    try:
        api.get_user(username)
    except tweepy.error.TweepError as resp:
        if resp.api_code == 50:
            return {'error': resp.args[0][0]['message']}

    tweets = []
    try:
        tweets = api.user_timeline(screen_name=username,
                                   count=settings.NUM_OF_TWEET)
    except tweepy.TweepError as msg:
        logging.error(msg)

    # store tweet information: username,
    # tweet id, date/time, text in database

    for tweet in tweets:
        get_or_create_tweet(tweet)

    logging.info('{} - tweets digested'.format(len(tweets)))
    return None


def get_or_create_tweet(tweet):
    """
    This method is responsible for creating tweet in the database.
    :param tweet: status object of tweepy
    :return: tweet object instance
    """
    tweet_obj, created = models.Tweet.objects.get_or_create(
        tweet_id=tweet.id_str)
    if created:
        tweet_obj.username = tweet.user.screen_name
        tweet_obj.text = tweet.text
        tweet_obj.tweet_on = tweet.created_at
        tweet_obj.image = tweet.user.profile_image_url
        if hasattr(tweet, 'retweeted_status'):
                tweet_obj.retweeted_user = tweet.retweeted_status.author.\
                    screen_name
                tweet_obj.retweeted_user_image = tweet.retweeted_status.\
                    author.profile_image_url
        tweet_obj.save()
    return tweet_obj
