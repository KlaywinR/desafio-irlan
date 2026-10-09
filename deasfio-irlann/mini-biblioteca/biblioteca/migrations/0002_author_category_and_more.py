from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("biblioteca", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Author",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("nationality", models.CharField(blank=True, max_length=60)),
            ],
            options={
                "verbose_name": "autor",
                "verbose_name_plural": "autores",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, unique=True)),
            ],
            options={
                "verbose_name": "categoria",
                "verbose_name_plural": "categorias",
            },
        ),
        migrations.AddField(
            model_name="book",
            name="categories",
            field=models.ManyToManyField(blank=True, related_name="books", to="biblioteca.category"),
        ),
        migrations.AddField(
            model_name="book",
            name="author_new",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="books",
                to="biblioteca.author",
            ),
        ),
    ]
