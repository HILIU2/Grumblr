from django.conf.urls import include, url

import django.contrib.auth.views
import grumblr.views

urlpatterns = [
    url(r'^login$', django.contrib.auth.views.login, {'template_name':'grumblr/login.html'}, name='login'),
    url(r'^logout$', django.contrib.auth.views.logout_then_login, name='logout'),
    url(r'^register$', grumblr.views.register, name="register"),
    url(r'^photo/(?P<user_name>\w+)$', grumblr.views.get_photo, name="photo"),
    url(r'^post/(?P<last_post>\d+)$', grumblr.views.post, name="post"),
    url(r'^profile/(?P<user_name>\w+)', grumblr.views.profile, name="profile"),
    url(r'^edit$', grumblr.views.load_profileEditing, name="load_profile"),
    url(r'^follow/(?P<user_name>\w+)$', grumblr.views.follow, name="follow"),
    url(r'^following$', grumblr.views.following, name="following"),
    url(r'^unfollow/(?P<user_name>\w+)$', grumblr.views.unfollow, name="unfollow"),
    url(r'^editprofile$', grumblr.views.changeProfile, name="change_profile"),
    url(r'^change_password$', grumblr.views.changePassword, name="change_password"),
    url(r'^confirmEmail/(?P<user_name>\w+)/(?P<token>\w+)', grumblr.views.confirm,  name="confirm"),
    url(r'^$', grumblr.views.home, name="home"),
    url(r'^forget_password$', grumblr.views.forget_password, name="forget_password"),
    url(r'^reset_password_email$', grumblr.views.reset_password_email, name="reset_password_email"),
    url(r'^reset_password/(?P<user_name>\w+)$', grumblr.views.reset_password, name="reset_password"),
    url(r'^addComment/(?P<status_id>\w+)$', grumblr.views.addComment, name="addComment"),
    url(r'^refreshComment/(?P<last_comment>\d+)$', grumblr.views.refreshComment, name="refreshComment"),
    url(r'^loadNewStatus/(?P<last_post>\d+)$', grumblr.views.loadNewStatus, name="loadNewStatus"),
    url(r'^loadNewComment/(?P<user_name>\w+)/(?P<last_comment>\d+)$', grumblr.views.selfNewComment, name="selfNewComment"),
    url(r'^refreshFollowing/(?P<last_post>\d+)$', grumblr.views.refreshFollowing, name="refreshFollowing"),
    url(r'^refreshFollowingComments/(?P<last_comment>\d+)$', grumblr.views.refreshFollowingComments, name="refreshFollowingComments"),
]
