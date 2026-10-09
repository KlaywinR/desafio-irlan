from django.contrib import admin
from .models import Author, Book, Category

class BookInline(admin.TabularInline):
    """Livros do autor na página do autor."""
    model = Book.authors.through
    fk_name = "author"
    extra = 1  
    can_delete = False
    verbose_name = "livro"
    verbose_name_plural = "livros"

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "nationality")
    search_fields = ("name",)
    inlines = [BookInline]

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.exclusive_books().exists():
            return False
        return super().has_delete_permission(request, obj)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "authors_list", "year_of_publication", "available")
    search_fields = ("title", "authors__name")
    list_filter = ("available", "categories")
    filter_horizontal = ("authors", "categories")

    @admin.display(description="Autores")
    def authors_list(self, obj):
        return ", ".join(author.name for author in obj.authors.all())

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("authors")
