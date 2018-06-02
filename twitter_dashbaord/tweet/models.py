from django.db import models
from django.utils import timezone


class Tweet(models.Model):
    tweet_id = models.CharField(max_length=30)
    username = models.CharField(max_length=100)
    text = models.CharField(max_length=800)
    image = models.CharField(max_length=200)
    tweet_on = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    retweeted_user = models.CharField(max_length=100, blank=True, null=True)
    retweeted_user_image = models.CharField(max_length=200,
                                            blank=True, null=True)

    def __unicode__(self):
        return self.text
