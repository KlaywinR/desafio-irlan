from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ("biblioteca", "0003_migrate_author_data"),
    ]

    operations = [
        migrations.RemoveField(model_name="book", name="author"),
        migrations.RenameField(model_name="book", old_name="author_new", new_name="author"),
        migrations.AlterField(
            model_name="book",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="books",
                to="biblioteca.author",
            ),
        ),
    ]
