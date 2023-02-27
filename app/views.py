from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


def sign_up(request):
    """
    URL: /sign_up/
    Renders a form that registers a new user.
    """

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            username = data['username']
            password = data['password1']

            User.objects.create_user(username=username, password=password)

            return HttpResponseRedirect('/')

    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})