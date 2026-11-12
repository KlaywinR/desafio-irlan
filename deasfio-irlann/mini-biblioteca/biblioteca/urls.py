from django.urls import path

from .views import author_create, author_detail, book_form, book_list

urlpatterns = [
    path("", book_list, name="book_list"),
    path("autores/novo/", author_create, name="author_create"),
    path("autores/<int:pk>/", author_detail, name="author_detail"),
    path("livros/novo/", book_form, name="book_create"),
    path("livros/<int:pk>/editar/", book_form, name="book_edit"),
]
