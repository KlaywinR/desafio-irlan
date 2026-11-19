from django.db import models
from django.db.models import Count, ProtectedError
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    RegexValidator,
)

from .validators import validar_ano_publicacao, validar_tamanho_arquivo


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
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(3, "O título deve ter pelo menos 3 caracteres.")],
    )
    authors = models.ManyToManyField(Author, related_name="books")
    categories = models.ManyToManyField(Category, blank=True, related_name="books")
    year_of_publication = models.IntegerField(validators=[validar_ano_publicacao])
    available = models.BooleanField(default=True)
    pages = models.PositiveIntegerField(
        "Páginas",
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1, "O livro deve ter pelo menos 1 página."),
            MaxValueValidator(5000, "O livro pode possuir no máximo 5000 páginas."),
        ],
    )
    isbn = models.CharField(
        "ISBN",
        blank=True,
        max_length=13,
        validators=[
            RegexValidator(r"^\d{13}$", "O ISBN deve possuir exatamente 13 dígitos numéricos."),
        ],
    )
    capa = models.ImageField(
        "Capa",
        upload_to="capas/",
        blank=True,
        validators=[
            validar_tamanho_arquivo,
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"]),
        ],
    )

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
