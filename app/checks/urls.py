
from django.urls import path
from . import views

urlpatterns = [
    path("", views.root, name="root"),
    path("check", views.check_page, name="check"),
    path("link/create", views.create_link, name="create_link"),
    path("p/<uuid:uuid>", views.personal_page, name="personal_page"),
]
