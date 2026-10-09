from django.db import models
from django.db.models import Count, ProtectedError
from django.db.models.signals import pre_delete
from django.dispatch import receiver

class Author(models.Model):
    name = models.CharField(max_length=120)
    nationality = models.CharField(max_length=60, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "autor"
        verbose_name_plural = "autores"

    def __str__(self):
        return self.name

    def exclusive_books(self):
        so_um_autor = Book.objects.annotate(n_authors=Count("authors")).filter(n_authors=1)
        return Book.objects.filter(pk__in=so_um_autor.values("pk"), authors=self)

class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        verbose_name = "categoria"
        verbose_name_plural = "categorias"

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(Author, related_name="books")
    categories = models.ManyToManyField(Category, blank=True, related_name="books")
    year_of_publication = models.IntegerField()
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.title

@receiver(pre_delete, sender=Author)
def impedir_apagar_ultimo_autor(sender, instance, **kwargs):
    orfaos = instance.exclusive_books()
    if orfaos.exists():
        titulos = ", ".join(b.title for b in orfaos)
        raise ProtectedError(
            f"Não é possível apagar '{instance.name}': ele é o único autor de: {titulos}.",
            set(orfaos),
        )
