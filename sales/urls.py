from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("invoice/<int:id>/pdf", views.pdf_rechnung, name="makePDF"),
    path("invoice/<int:id>/kaufvertrag", views.pdf_kaufvertrag, name="makePDFContract"),
]