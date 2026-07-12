"""RedirectRule CRUD routes, mounted at the root as ``/url/``."""

from rest_framework.routers import SimpleRouter

from apps.rules.api.views import RedirectRuleViewSet

# SimpleRouter (not DefaultRouter): no browsable "Api Root" view at the mount point,
# which here is the site root — `/` is handled by config.urls instead.
router = SimpleRouter()
router.register("url", RedirectRuleViewSet, basename="url")

urlpatterns = router.urls