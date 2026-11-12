from django.shortcuts import get_object_or_404, redirect, render

from .forms import AuthorForm, BookForm
from .models import Author, Book


def book_list(request):
    books = Book.objects.prefetch_related("authors")

    context = {
        "books": books,
    }

    return render(request, "book_list.html", context)


def author_create(request):
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save()
            return redirect("author_detail", pk=author.pk)
    else:
        form = AuthorForm()

    return render(request, "author_form.html", {"form": form})


def author_detail(request, pk):
    author = get_object_or_404(Author, pk=pk)
    books = author.books.all()

    context = {
        "author": author,
        "books": books,
    }

    return render(request, "author_detail.html", context)


def book_form(request, pk=None):
    book = get_object_or_404(Book, pk=pk) if pk is not None else None
    data = request.POST if request.method == "POST" else None
    form = BookForm(data, instance=book)

    if request.method == "POST" and form.is_valid():
        book = form.save()
        author = book.authors.first()
        return redirect("author_detail", pk=author.pk)

    return render(
        request,
        "book_form.html",
        {
            "form": form,
            "is_editing": book is not None,
        },
    )
