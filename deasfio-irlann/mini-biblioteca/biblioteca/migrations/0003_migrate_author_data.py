from django.db import migrations

def texto_para_author(apps, schema_editor):
    Book = apps.get_model("biblioteca", "Book")
    Author = apps.get_model("biblioteca", "Author")

    for book in Book.objects.all():
        nome = book.author.strip()
        author, _ = Author.objects.get_or_create(name=nome)
        book.author_new = author
        book.save(update_fields=["author_new"])
        
def author_para_texto(apps, schema_editor):
    Book = apps.get_model("biblioteca", "Book")
    for book in Book.objects.select_related("author_new"):
        if book.author_new:
            book.author = book.author_new.name
            book.save(update_fields=["author"])

class Migration(migrations.Migration):
    dependencies = [
        ("biblioteca", "0002_author_category_and_more"),
    ]

    operations = [
        migrations.RunPython(texto_para_author, author_para_texto),
    ]
