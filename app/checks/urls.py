
from django.urls import path
from . import views

urlpatterns = [
    path("", views.root, name="root"),
    path("check", views.check_page, name="check"),
    path("link/create", views.create_link, name="create_link"),
    path("check/<uuid:token>/", views.user_check_list, name="user_check_list"),
]
