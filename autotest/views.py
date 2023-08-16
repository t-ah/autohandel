from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("<a href=\"admin\">Weiter zur App</a>")