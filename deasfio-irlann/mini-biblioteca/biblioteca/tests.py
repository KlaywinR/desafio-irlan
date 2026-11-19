from io import BytesIO
import tempfile

from django.db import transaction
from django.db.models import ProtectedError
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from .forms import BookForm
from .models import Author, Book, Category
from .validators import validar_tamanho_arquivo


class BookValidationTests(TestCase):
    def make_book(self, **overrides):
        values = {
            "title": "Livro válido",
            "year_of_publication": 2000,
            "pages": 1,
            "isbn": "",
        }
        values.update(overrides)
        return Book(**values)

    def test_title_requires_at_least_three_characters(self):
        with self.assertRaises(ValidationError):
            self.make_book(title="AB").full_clean()

    def test_publication_year_is_between_1450_and_current_year(self):
        self.make_book(year_of_publication=1450).full_clean()
        self.make_book(year_of_publication=timezone.localdate().year).full_clean()

        with self.assertRaises(ValidationError):
            self.make_book(year_of_publication=1449).full_clean()
        with self.assertRaises(ValidationError):
            self.make_book(year_of_publication=timezone.localdate().year + 1).full_clean()

    def test_pages_are_optional_and_limited_to_1_through_5000(self):
        self.make_book(pages=None).full_clean()
        self.make_book(pages=5000).full_clean()

        with self.assertRaises(ValidationError):
            self.make_book(pages=0).full_clean()
        with self.assertRaises(ValidationError):
            self.make_book(pages=5001).full_clean()

    def test_isbn_is_optional_but_requires_thirteen_digits(self):
        self.make_book(isbn="").full_clean()
        self.make_book(isbn="1234567890123").full_clean()

        with self.assertRaises(ValidationError):
            self.make_book(isbn="123456789012").full_clean()
        with self.assertRaises(ValidationError):
            self.make_book(isbn="123456789012a").full_clean()


class CoverUploadTests(TestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.media_dir.cleanup)
        override = override_settings(MEDIA_ROOT=self.media_dir.name)
        override.enable()
        self.addCleanup(override.disable)

    def make_image(self, name="capa.png", image_format="PNG"):
        image_bytes = BytesIO()
        Image.new("RGB", (2, 2), color="red").save(image_bytes, format=image_format)
        return SimpleUploadedFile(
            name,
            image_bytes.getvalue(),
            content_type=f"image/{image_format.lower()}",
        )

    def test_cover_size_limit_is_one_megabyte(self):
        validar_tamanho_arquivo(SimpleUploadedFile("capa.jpg", b"x" * (1024 * 1024)))
        with self.assertRaises(ValidationError):
            validar_tamanho_arquivo(
                SimpleUploadedFile("capa.jpg", b"x" * (1024 * 1024 + 1))
            )

    def test_cover_must_be_an_allowed_image(self):
        author = Author.objects.create(name="Autora")
        form_data = {
            "title": "Livro com capa",
            "authors": [author.pk],
            "year_of_publication": 2000,
            "available": "on",
        }

        invalid_extension = BookForm(form_data, {"capa": self.make_image("capa.gif")})
        self.assertFalse(invalid_extension.is_valid())
        self.assertIn("capa", invalid_extension.errors)

        invalid_content = SimpleUploadedFile(
            "capa.png",
            b"isto nao e uma imagem",
            content_type="image/png",
        )
        invalid_image = BookForm(form_data, {"capa": invalid_content})
        self.assertFalse(invalid_image.is_valid())
        self.assertIn("capa", invalid_image.errors)

    def test_missing_file_data_is_accepted_for_optional_cover(self):
        author = Author.objects.create(name="Autora")
        form = BookForm(
            {
                "title": "Livro sem arquivo",
                "authors": [author.pk],
                "year_of_publication": 2000,
                "available": "on",
            }
        )

        self.assertTrue(form.is_valid())
        self.assertFalse(form.cleaned_data["capa"])
        self.assertContains(
            self.client.get(reverse("book_create")),
            'enctype="multipart/form-data"',
        )

    def test_cover_upload_is_saved_and_rendered(self):
        author = Author.objects.create(name="Autora")
        response = self.client.post(
            reverse("book_create"),
            {
                "title": "Livro com capa",
                "authors": [author.pk],
                "year_of_publication": 2000,
                "available": "on",
                "capa": self.make_image(),
            },
        )

        book = Book.objects.get(title="Livro com capa")
        self.assertRedirects(response, reverse("author_detail", args=[author.pk]))
        self.assertTrue(book.capa.name.startswith("capas/"))
        self.assertContains(self.client.get(reverse("book_list")), book.capa.url)
        self.assertContains(
            self.client.get(reverse("author_detail", args=[author.pk])),
            book.capa.url,
        )


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
        self.assertContains(
            response,
            f'href="{reverse("book_edit", args=[self.book.pk])}?author_id={self.a2.pk}"',
        )

    def test_author_detail_404(self):
        self.assertEqual(self.client.get(reverse("author_detail", args=[9999])).status_code, 404)

    def test_lista_tem_link_para_criar_autor(self):
        response = self.client.get(reverse("book_list"))
        self.assertContains(
            response,
            f'href="{reverse("author_create")}"',
        )
        self.assertContains(response, "Novo autor")
        self.assertContains(
            response,
            f'href="{reverse("book_create")}"',
        )
        self.assertContains(
            response,
            f'href="{reverse("book_edit", args=[self.book.pk])}"',
        )

    def test_formulario_novo_autor_mostra_campos_individuais_e_csrf(self):
        response = self.client.get(reverse("author_create"))
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, "<label for=\"id_name\">Nome:</label>")
        self.assertContains(
            response,
            "<label for=\"id_nationality\">Nacionalidade:</label>",
        )

    def test_formulario_invalido_exibe_erro_junto_ao_nome(self):
        response = self.client.post(
            reverse("author_create"),
            {"name": "", "nationality": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este campo é obrigatório.")
        self.assertEqual(Author.objects.filter(name="").count(), 0)

    def test_cria_autor_sem_nacionalidade_e_redireciona_sem_duplicar(self):
        response = self.client.post(
            reverse("author_create"),
            {"name": "Clarice Lispector", "nationality": ""},
        )

        self.assertRedirects(
            response,
            reverse("author_detail", args=[Author.objects.get(name="Clarice Lispector").pk]),
        )
        self.assertEqual(Author.objects.filter(name="Clarice Lispector").count(), 1)

        self.client.get(response["Location"])
        self.assertEqual(Author.objects.filter(name="Clarice Lispector").count(), 1)

    def test_post_sem_token_csrf_retorna_403_e_nao_cria_autor(self):
        client = Client(enforce_csrf_checks=True)
        client.get(reverse("author_create"))

        response = client.post(
            reverse("author_create"),
            {"name": "Autor sem token", "nationality": ""},
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Author.objects.filter(name="Autor sem token").exists())

    def test_cria_livro_normaliza_titulo_e_aceita_sem_categoria(self):
        response = self.client.post(
            reverse("book_create"),
            {
                "title": "  Livro   novo ",
                "authors": [self.a1.pk],
                "year_of_publication": 2024,
                "available": "on",
            },
        )

        book = Book.objects.get(title="Livro novo")
        self.assertRedirects(
            response,
            reverse("author_detail", args=[self.a1.pk]),
        )
        self.assertEqual(book.categories.count(), 0)

    def test_titulo_curto_e_ano_futuro_sao_exibidos_no_formulario(self):
        response = self.client.post(
            reverse("book_create"),
            {
                "title": " a ",
                "authors": [self.a1.pk],
                "year_of_publication": timezone.localdate().year + 1,
                "available": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "O título deve ter pelo menos 3 caracteres")
        self.assertContains(response, "O ano de publicação não pode ser futuro")
        self.assertEqual(Book.objects.count(), 1)

    def test_edita_livro_existente_e_livro_inexistente_retorna_404(self):
        response = self.client.get(reverse("book_edit", args=[self.book.pk]))

        self.assertContains(response, "Editar livro")
        self.assertContains(response, 'value="Livro Coautoria"')
        self.assertEqual(
            self.client.get(reverse("book_edit", args=[9999])).status_code,
            404,
        )

    def test_salva_edicao_e_redireciona_para_pagina_do_autor(self):
        response = self.client.post(
            reverse("book_edit", args=[self.book.pk]),
            {
                "title": "Livro atualizado",
                "authors": [self.a2.pk],
                "year_of_publication": 2021,
                "available": "on",
            },
        )

        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Livro atualizado")
        self.assertEqual(
            response["Location"],
            reverse("author_detail", args=[self.a2.pk]),
        )

    def test_edita_com_coautoria_e_retorna_ao_autor_de_origem(self):
        response = self.client.post(
            f'{reverse("book_edit", args=[self.book.pk])}?author_id={self.a2.pk}',
            {
                "title": "Livro atualizado",
                "authors": [self.a1.pk, self.a2.pk],
                "year_of_publication": 2021,
                "available": "on",
            },
        )

        self.assertRedirects(
            response,
            reverse("author_detail", args=[self.a2.pk]),
        )
        self.book.refresh_from_db()
        self.assertEqual(self.book.authors.count(), 2)

    def test_lista_ordena_por_titulo_e_informa_contagens(self):
        Book.objects.create(
            title="A primeira obra",
            year_of_publication=2001,
            available=False,
        )

        response = self.client.get(reverse("book_list"))

        self.assertEqual(
            list(response.context["books"].values_list("title", flat=True)),
            ["A primeira obra", "Livro Coautoria"],
        )
        self.assertEqual(response.context["total_books"], 2)
        self.assertEqual(response.context["available_books"], 1)

    def test_sobre_exibe_total_e_livros_disponiveis(self):
        Book.objects.create(
            title="Indisponível",
            year_of_publication=2001,
            available=False,
        )

        response = self.client.get(reverse("sobre"))

        self.assertContains(response, "Total de livros: 2")
        self.assertContains(response, "Livros disponíveis: 1")

    def test_exclusao_so_ocorre_no_post_e_retorna_404_para_livro_inexistente(self):
        delete_url = reverse("book_delete", args=[self.book.pk])
        response = self.client.get(delete_url)

        self.assertContains(response, "Tem certeza de que deseja excluir")
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())
        self.assertEqual(self.client.get(reverse("book_delete", args=[9999])).status_code, 404)

        response = self.client.post(delete_url)

        self.assertRedirects(response, reverse("book_list"))
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())
