from django.urls import path

from .views import PollRunList

app_name = "polling"

urlpatterns = [
    path("runs/", PollRunList.as_view(), name="poll-run-list"),
]
