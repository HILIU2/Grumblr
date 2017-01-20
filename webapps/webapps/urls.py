from django.conf.urls import include, url

import grumblr.views

urlpatterns = [
    url(r'^grumblr/', include('grumblr.urls')),
    url(r'^$', grumblr.views.home),
]
