from django.urls import re_path
from pretalx.event.models.event import SLUG_REGEX

from .views import VimeoSettings, api_list, api_single

urlpatterns = [
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/settings/p/vimeo/$",
        VimeoSettings.as_view(),
        name="settings",
    ),
    re_path(
        rf"^api/events/(?P<event>{SLUG_REGEX})/p/vimeo/$",
        api_list,
        name="api_list",
    ),
    re_path(
        rf"^api/events/(?P<event>{SLUG_REGEX})/submissions/(?P<code>[A-Z0-9]+)/p/vimeo/$",
        api_single,
        name="api_single",
    ),
]
