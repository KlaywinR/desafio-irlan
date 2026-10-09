from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
   
    dependencies = [
        ("biblioteca", "0004_book_author_fk"),
    ]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="author",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="biblioteca.author",
            ),
        ),
        migrations.AddField(
            model_name="book",
            name="authors",
            field=models.ManyToManyField(related_name="books", to="biblioteca.author"),
        ),
    ]
