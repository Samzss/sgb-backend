from django.urls import path

from . import views

urlpatterns = [
    path("health", views.HealthView.as_view()),
    path("collections", views.CollectionsView.as_view()),
    path("resources", views.ResourceListView.as_view()),
    path("resources/<str:code>", views.ResourceDetailView.as_view()),
]
