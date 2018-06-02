from social_core.exceptions import AuthForbidden

from django.shortcuts import render


class CustomSocialAuthExceptionMiddleware(object):

    def process_exception(self, request, exception):
        if isinstance(exception, AuthForbidden):
            return render(request, 'error-page.html')
