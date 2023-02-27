from django.shortcuts import render


def index(request):
    """
    URL: /
    Renders home page.
    """

    return render(request, "home/index.html")
