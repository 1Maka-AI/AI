# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 23:23:00 2024

@author: kingo
"""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.ask_api, name="ask"),
]