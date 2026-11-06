from django.shortcuts import get_object_or_404, redirect, render

from .forms import AuthorForm
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
