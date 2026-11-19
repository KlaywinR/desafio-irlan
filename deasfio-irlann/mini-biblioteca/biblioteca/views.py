from django.db.models import Count, Q
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import AuthorForm, BookForm
from .models import Author, Book


def book_counts():
    return Book.objects.aggregate(
        total_books=Count("pk"),
        available_books=Count("pk", filter=Q(available=True)),
    )


class BookListView(ListView):
    model = Book
    template_name = "book_list.html"
    context_object_name = "books"
    ordering = ["title"]

    def get_queryset(self):
        return super().get_queryset().prefetch_related("authors").order_by("title")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(book_counts())
        return context


class AuthorCreateView(CreateView):
    model = Author
    form_class = AuthorForm
    template_name = "author_form.html"
    context_object_name = "author"
    success_url = reverse_lazy("book_list")

    def get_success_url(self):
        return reverse("author_detail", kwargs={"pk": self.object.pk})


class AuthorDetailView(DetailView):
    model = Author
    template_name = "author_detail.html"
    context_object_name = "author"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["books"] = self.object.books.order_by("title").prefetch_related("authors")
        return context


class BookAuthorRedirectMixin:
    success_url = reverse_lazy("book_list")

    def get_success_url(self):
        author_id = self.request.GET.get("author_id", "")
        author = (
            Author.objects.filter(pk=author_id).first()
            if author_id.isdecimal()
            else None
        )
        if author is None:
            author = self.object.authors.first()
        if author is None:
            return super().get_success_url()
        return reverse("author_detail", kwargs={"pk": author.pk})


class BookCreateView(BookAuthorRedirectMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = "book_form.html"
    context_object_name = "book"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_editing"] = False
        return context


class BookUpdateView(BookAuthorRedirectMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = "book_form.html"
    context_object_name = "book"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_editing"] = True
        return context


class BookDeleteView(DeleteView):
    model = Book
    template_name = "livro_confirm_delete.html"
    context_object_name = "book"
    success_url = reverse_lazy("book_list")


class AboutView(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(book_counts())
        return context
