from django.urls import path

# 把app的view函數include進來，把view丟給url
from home.views import *
urlpatterns = [
    path('',home,name='home'),
    path('request/makemove',makemove,name='makemove'),
    path('request/getmove',getmove,name='getmove'),
]
