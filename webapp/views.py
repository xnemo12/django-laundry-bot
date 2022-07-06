from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, "webapp/index.html")


def slider(request):
    return render(request, "webapp/slider.html")


def slider_mobile(request):
    return render(request, "webapp/slider-mobile.html")
