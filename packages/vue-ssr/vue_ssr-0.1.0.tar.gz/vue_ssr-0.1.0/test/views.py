from django.shortcuts import render


def root(request):
    return render(request, "example/example.html", {"username": request.user.username})
