from django.shortcuts import render


def logout(request):
    return render(request, 'registration/login.html')
