from django.urls import re_path
from pretalx.event.models.event import SLUG_REGEX

from . import views

urlpatterns = [
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/settings/p/public_voting/$",
        views.PublicVotingSettingsView.as_view(),
        name="settings",
    ),
    re_path(
        f"^(?P<event>{SLUG_REGEX})/p/voting/signup/$",
        views.SignupView.as_view(),
        name="signup",
    ),
    re_path(
        f"^(?P<event>{SLUG_REGEX})/p/voting/thanks/$",
        views.ThanksView.as_view(),
        name="thanks",
    ),
    re_path(
        f"^(?P<event>{SLUG_REGEX})/p/voting/talks/(?P<signed_user>[^/]+)/$",
        views.SubmissionListView.as_view(),
        name="talks",
    ),
]
