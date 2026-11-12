from django import forms
from django.utils import timezone

from .models import Author, Book


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ["name", "nationality"]
        labels = {
            "name": "Nome",
            "nationality": "Nacionalidade",
        }
        error_messages = {
            "name": {
                "required": "Este campo é obrigatório.",
            },
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            "title",
            "authors",
            "year_of_publication",
            "available",
            "categories",
        ]
        labels = {
            "title": "Título",
            "authors": "Autores",
            "year_of_publication": "Ano de publicação",
            "available": "Disponível",
            "categories": "Categorias",
        }
        widgets = {
            "categories": forms.CheckboxSelectMultiple,
        }
        error_messages = {
            "title": {
                "required": "Informe o título do livro.",
            },
            "authors": {
                "required": "Selecione pelo menos um autor.",
            },
            "year_of_publication": {
                "required": "Informe o ano de publicação.",
                "invalid": "Informe um ano válido.",
            },
        }

    def clean_title(self):
        title = " ".join(self.cleaned_data["title"].split())
        if len(title) < 3:
            raise forms.ValidationError(
                "Sistema: O título da obra deve possuir ao menos 3 caracteres após os espaços extras serem removidos."
            )
        return title

    def clean_year_of_publication(self):
        year = self.cleaned_data["year_of_publication"]
        if year > timezone.localdate().year:
            raise forms.ValidationError(
                "Sistema: O ano da publicação do livro não pode ser futuro. Por favor, Informe o ano atual ou um ano anterior."
            )
        return year
