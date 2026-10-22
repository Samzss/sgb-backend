from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter(trailing_slash=False)
router.register("users", views.UserViewSet)
router.register("loans", views.LoanViewSet)
router.register("reservations", views.ReservationViewSet)
router.register("fines", views.FineViewSet)

urlpatterns = [path("health", views.HealthView.as_view()), path("", include(router.urls))]
