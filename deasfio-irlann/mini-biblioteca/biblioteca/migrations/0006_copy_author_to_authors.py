from django.db import migrations

AUTOR_DESCONHECIDO = "Autor desconhecido"


def copiar_fk_para_m2m(apps, schema_editor):
    Book = apps.get_model("biblioteca", "Book")
    for book in Book.objects.exclude(author__isnull=True):
        book.authors.add(book.author_id)

def copiar_m2m_para_fk(apps, schema_editor):
    Book = apps.get_model("biblioteca", "Book")
    Author = apps.get_model("biblioteca", "Author")
    Through = Book.authors.through

    for book in Book.objects.all():
        primeiro = Through.objects.filter(book_id=book.pk).order_by("id").first()
        if primeiro:
            book.author_id = primeiro.author_id
        else:
            coringa, _ = Author.objects.get_or_create(name=AUTOR_DESCONHECIDO)
            book.author_id = coringa.pk
        book.save(update_fields=["author"])

class Migration(migrations.Migration):
    dependencies = [
        ("biblioteca", "0005_book_authors_m2m"),
    ]

    operations = [
        migrations.RunPython(copiar_fk_para_m2m, copiar_m2m_para_fk),
    ]
