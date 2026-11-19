from django.urls import path

from .views import (
    AboutView,
    AuthorCreateView,
    AuthorDetailView,
    BookCreateView,
    BookDeleteView,
    BookListView,
    BookUpdateView,
)

urlpatterns = [
    path("", BookListView.as_view(), name="book_list"),
    path("autores/novo/", AuthorCreateView.as_view(), name="author_create"),
    path("autores/<int:pk>/", AuthorDetailView.as_view(), name="author_detail"),
    path("livros/novo/", BookCreateView.as_view(), name="book_create"),
    path("livros/<int:pk>/editar/", BookUpdateView.as_view(), name="book_edit"),
    path("livros/<int:pk>/excluir/", BookDeleteView.as_view(), name="book_delete"),
    path("sobre/", AboutView.as_view(), name="sobre"),
]
