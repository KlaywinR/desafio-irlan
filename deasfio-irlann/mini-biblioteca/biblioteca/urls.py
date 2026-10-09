from django.urls import path

from .views import author_detail, book_list

urlpatterns = [
    path("", book_list, name="book_list"),
    path("autores/<int:pk>/", author_detail, name="author_detail"),
]
