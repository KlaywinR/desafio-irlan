from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("biblioteca", "0006_copy_author_to_authors"),
    ]

    operations = [
        migrations.RemoveField(model_name="book", name="author"),
    ]
