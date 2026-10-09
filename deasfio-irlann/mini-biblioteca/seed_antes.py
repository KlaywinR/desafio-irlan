"""Cadastra livros de exemplo para chegar a 10 livros ANTES do desafio.

Rode ANTES de aplicar as migrações 0005 a 0007 (enquanto Book ainda tem a FK `author`):

    python manage.py shell -c "exec(open('seed_antes.py', encoding='utf-8').read())"
"""
from biblioteca.models import Author, Book, Category

if not hasattr(Book, "author"):
    raise SystemExit("Este script é só para ANTES da migração para ManyToMany (Book.author não existe mais).")

dados = [
    ("Memórias Póstumas de Brás Cubas", "MACHADO DE ASSIS", 1881),
    ("Quincas Borba", "MACHADO DE ASSIS", 1891),
    ("Capitães da Areia", "JORGE AMADO", 1937),
    ("Gabriela, Cravo e Canela", "JORGE AMADO", 1958),
    ("São Bernardo", "GRACILIANO RAMOS", 1934),
    ("A Hora da Estrela", "CLARICE LISPECTOR", 1977),
    ("Grande Sertão: Veredas", "GUIMARÃES ROSA", 1956),
]
for titulo, nome, ano in dados:
    autor, _ = Author.objects.get_or_create(name=nome)
    Book.objects.get_or_create(title=titulo, defaults={"author": autor, "year_of_publication": ano})
print("Total de livros:", Book.objects.count())
