# Mini Biblioteca — livros com vários autores

Transição de `Book.author` uma chave estrangeira para `Book.authors` a relação  ManyToManyField, sem apagar o banco e sem perder nenhum vínculo livro e autor.

## Como rodar

```bash
# 0. BACKUP obrigatório antes de mexer em migrações
copy db.sqlite3 db.backup.sqlite3        )

# 1. Antes das miigrações novas, deve-se ter pelo menos 10 livros.
python manage.py shell -c "exec(open('seed_antes.py', encoding='utf-8').read())"

# 2. aplicar a transição:
python manage.py migrate

# 3. conferir
python manage.py test
python manage.py runserver
```

## Migrações 

| Migração | O que faz |
|---|---|
| 0005_book_authors_m2m | Adiciona o ManyToMany em  authors mas author continua a existir
006_copy_author_to_authors | Copia os dados com RunPython: o autor de cada livro vira o 1º item de authors. Tem função de ida e de volta. |
| 0007_remove_book_author| Só agora remove a FK antiga. |

Dois ajustes na FK dentro da 0005:

- related_name="+": libera o nome books para o ManyToMany.
- null=True: sem isso, a migração não conseguiria ser revertida, pois recriar uma fk em uma tabela cheia é impossível.

## O que mudou no restante

- author_detail: nenhuma alteração. author.books.all() continua funcionando porque o ManyToMany usa o mesmo related_name="books", da antiga FK.
-Lista de livros: cada autor é um link para /autores/<id>/ (vários links por livro, separados por vírgula). A view trocou select_related("author") por prefecth_related_authors (única mudança de código fora do admin/models).
- Admin de Book: coluna Autores método authors_list, porque ManyToMany não pode ir direto em list_display; busca por title e authors__name; filter_horizontal em authors e categories.
-Admin de Author: inline dos livros usa a tabela intermediária (Book.authors.through).

## Respostas

### 1. Que dados se perdem quando a migração é revertida? Por quê?

Perdem-se os coautores. Reverter significa voltar de "um livro tem vários autores" para
"um livro tem um autor. Uma ForeignKey guarda um único valor; não há onde pôr o 2º e o 3º autor.
A função de volta copiar_m2m_para_fk guarda apenas o priemeiro valor vinculado ao livro- pela oredem em que os vinculos foram criados; ManytoMany não possui noção do autor principal, onde descarta os demais vínculos.


Dois detalhes que também alteram os dados na volta:

- Livro sem nenhum autor ossível com ManyToMany: a FK antiga era obrigatória, então ele recebe um autor-coringa "Autor desconhecido". A informação original "sem autor" se perde.
- A reversão não é uma inversa perfeita: migrate → reverter → migrate de novo não recupera coautores perdidos.

O que não se perde: os registros de Author, os Book e os vínculos de livros com um único autor.
(Testado: um livro com 3 autores voltou com 1; um livro sem autor voltou com "Autor desconhecido".)

### 2. O que acontece com um livro quando o seu único autor é apagado? Como garantir pelo menos um autor?

O que acontece (sem proteção): o livro continua existindo, sem nenhum autor. No ManyToMany não há ondelete no campo: o que existe é a tabela intermediária iblioteca_book_author, cujas linhas são apagadas e cascata junto com o autor. O livro não é afetado, e fica sozinho com a coluna "Autores" vazia. Ademais, nenhum erro é lançado.

Como garantir ≥ 1 autor o banco, sozinho, não consegue: não existe NOT NULL para "tem ao menos uma linha na tabela intermediári. A garantia vem em camadas, todas implementadas aqui:

1. Formulários: authors não tem blank=True, então admin e ModelForm exigem ao menos 1 autor ao criar ou editar um book.
 
2. Apagar autor: um sinal pre_delete em Author consulta author.exclusive_books() - livros em que ele é um único autor e lança ProtecterError se houver algum. Vale também para o shell em scripts. No admim, o botao de Apagar some para o autor.
 
3. Inline do autor com can_delete = False: desvincular por ali burlaria a regra. Para tirar um autor de um livro  edita-se o livro, onde o formulário valida. 


## Testes

```bash
python manage.py test
```
