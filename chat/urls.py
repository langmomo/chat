from django.urls import path, re_path

from django.conf.urls import url
from .views import ThreadView, InboxView, SignupView
app_name = 'chat'
urlpatterns = [
    path("", InboxView.as_view()),
    url("signup/", SignupView),
    re_path(r"^(?P<username>[\w.@+-]+)", ThreadView.as_view()),
    url(r'^ajax/validate_username/$',ThreadView.as_view()),
]
