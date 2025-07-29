from django.urls import path

from . import views

urlpatterns = [
    path("rooms/", views.MatrixRoomListView.as_view(), name="matrix_rooms"),
]
