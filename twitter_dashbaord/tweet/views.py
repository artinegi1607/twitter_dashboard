import json

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required

from tweet.tasks import stream_tweets
from . import models
from .tweets import get_tweets


@csrf_exempt
@login_required
def index(request):
    """
    This initiates methods to fetch tweets on the basis of given twitter
    handle.
    This initializes-
        get_tweets: method that fetch latest 200 tweets
        stream_tweets: this method starts a celery task that opens socket and
         starts streaming tweets
    :param request: http request
    :return:
    """
    template_name = 'home.html'
    if request.method == 'GET':
        username = request.GET.get('username', '')
        tweets = []
        if username:
            # fetch latest 200 tweets
            resp = get_tweets(username)

            if resp:
                error = resp.get('error', '')
                return render(
                    request, template_name=template_name,
                    context={'error': error}
                )

            # opens socket for live streaming
            stream_tweets.delay(username)
            tweets = models.Tweet.objects.filter(username__iexact=username).\
                order_by('-tweet_on')

        return render(
            request, template_name=template_name,
            context={'tweets': tweets, 'username': username}
        )


class ErrorView(TemplateView):
    template_name = 'error-page.html'


@login_required
def stream_view(request):
    """
    This view fetches tweets as per username from database,
     make json data available and return.
    :param request: http request
            - username : twitter handle
            - filter : live or history
    :return: Json data Response
    """
    if not request.method == 'GET':
        return HttpResponse({'data': "Method not allowed"})

    username = request.GET.get('username', '')
    _filter = request.GET.get('filter', '')
    tweets = None
    overall_tweets = models.Tweet.objects.filter(username__iexact=username).\
        order_by('-tweet_on')

    if _filter == 'live':
        tweets = overall_tweets[:20]
    elif _filter == 'history':
        tweets = overall_tweets[20:]
    else:
        tweets = overall_tweets

    out = []
    for tweet in tweets:
        username = tweet.retweeted_user if tweet.retweeted_user \
            else tweet.username
        image = tweet.retweeted_user_image if tweet.retweeted_user\
            else tweet.image
        res = [
            '@'+username,
            "<img height='100%' width='70%' src=" + image + " /img>",
            tweet.text,
            str(tweet.tweet_on)
        ]
        out.append(res)

    return HttpResponse(json.dumps({'data': out}))
