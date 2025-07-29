from django.urls import re_path
from pretalx.event.models.event import SLUG_REGEX

from .views import SalesforceSettingsView, SalesforceSyncView

urlpatterns = [
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/settings/p/pretalx_salesforce/$",
        SalesforceSettingsView.as_view(),
        name="settings",
    ),
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/settings/p/pretalx_salesforce/sync$",
        SalesforceSyncView.as_view(),
        name="sync",
    ),
]
