from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("invoice/<int:id>/pdf", views.pdf, name="makePDF"),
]