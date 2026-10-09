from django.db import transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse
from .models import Author, Book, Category

class ModelTests(TestCase):
    def setUp(self):
        self.a1 = Author.objects.create(name="Rachel de Queiroz")
        self.a2 = Author.objects.create(name="Jorge Amado")
        self.solo = Book.objects.create(title="O Quinze", year_of_publication=1930)
        self.solo.authors.add(self.a1)
        self.coautoria = Book.objects.create(title="Obra a Quatro Mãos", year_of_publication=2000)
        self.coautoria.authors.add(self.a1, self.a2)

    def test_str(self):
        self.assertEqual(str(self.a1), "Rachel de Queiroz")
        self.assertEqual(str(self.solo), "O Quinze")
        self.assertEqual(str(Category.objects.create(name="Romance")), "Romance")

    def test_livro_com_dois_autores(self):
        self.assertEqual(self.coautoria.authors.count(), 2)
        self.assertIn(self.coautoria, self.a1.books.all())
        self.assertIn(self.coautoria, self.a2.books.all())

    def test_nao_apaga_autor_unico_de_um_livro(self):
        with self.assertRaises(ProtectedError), transaction.atomic():
            self.a1.delete() 
        self.assertTrue(Author.objects.filter(pk=self.a1.pk).exists())

    def test_apaga_autor_que_tem_coautor(self):
        self.a2.delete() 
        self.assertEqual(list(self.coautoria.authors.all()), [self.a1])

    def test_autor_sem_livros_pode_ser_apagado(self):
        outro = Author.objects.create(name="Sem Livros")
        outro.delete()
        self.assertFalse(Author.objects.filter(pk=outro.pk).exists())

class ViewTests(TestCase):
    def setUp(self):
        self.a1 = Author.objects.create(name="Autor Um")
        self.a2 = Author.objects.create(name="Autor Dois")
        self.book = Book.objects.create(title="Livro Coautoria", year_of_publication=2020)
        self.book.authors.add(self.a1, self.a2)

    def test_lista_tem_link_para_cada_autor(self):
        response = self.client.get(reverse("book_list"))
        for autor in (self.a1, self.a2):
            self.assertContains(response, f'href="{reverse("author_detail", args=[autor.pk])}"')

    def test_author_detail_lista_livros(self):
        response = self.client.get(reverse("author_detail", args=[self.a2.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Livro Coautoria")

    def test_author_detail_404(self):
        self.assertEqual(self.client.get(reverse("author_detail", args=[9999])).status_code, 404)
