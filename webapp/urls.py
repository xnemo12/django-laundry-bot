from django.urls import path
from webapp.views import index, slider, slider_mobile

urlpatterns = [
    path('', index, name='home'),
    path('slider', slider, name='slider'),
    path('slider-mobile', slider_mobile, name='slider-mobile')
]