Migração da Mini Biblioteca para PostgreSQL

Diferenças entre SQLite e PostgreSQL

SQLite é um banco embarcado em arquivo local. Não exige um processo de servidor separado, é simples para desenvolvimento, testes e aplicações pequenas, mas possui menos recursos de administração e concorrência para cargas reais. PostgreSQL é um servidor de banco relacional cliente-servidor, indicado para sistemas com concorrência, usuários distintos, permissões granulares, disponibilidade e recursos avançados.

Use SQLite em protótipos, scripts locais e ambientes simples; use PostgreSQL em aplicação real, múltiplos processos ou servidores, produção e cenários com requisitos mais fortes de concorrência e administração.

Driver do Django

Django usa o backend django.db.backends.postgresql. Para essa conexão ele precisa de psycopg 3, recomendado pela documentação atual, ou psycopg2. Neste projeto foi instalado o pacote binário:

python -m pip install "psycopg[binary]>=3.2"

A dependência também está registrada em requirements.txt.

Chaves de DATABASES

ENGINE seleciona o backend Django; no projeto é django.db.backends.postgresql.

NAME é o nome do banco.

USER é o papel ou usuário que faz a conexão.

PASSWORD é a senha do usuário da aplicação.

HOST é o endereço do servidor, como localhost.

PORT é a porta TCP do PostgreSQL, normalmente 5432.

Criação segura do banco

O superusuário postgres só deve ser usado pelo administrador. Para a aplicação, execute o conteúdo de criar_banco_postgresql.sql como administrador e substitua a senha fictícia antes da execução:

CREATE ROLE biblioteca_user LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD 'senha_forte';
CREATE DATABASE biblioteca_db OWNER biblioteca_user ENCODING 'UTF8';

Em seguida, configure um .env local com biblioteca_user, nunca com postgres.

Variáveis de ambiente

Variáveis de ambiente são pares nome e valor fornecidos ao processo sem serem inseridos diretamente no código-fonte. Senhas não devem ser escritas no código porque podem ser copiadas em commits, histórico Git, logs e builds.

O projeto usa python-decouple. O settings lê o .env com config('NOME'); variáveis que precisam de conversão usam cast=bool ou cast=Csv().

Outras informações sensíveis ou dependentes do ambiente são SECRET_KEY, DEBUG, ALLOWED_HOSTS e todas as credenciais da seção DATABASES.

Antes e depois

Antes, o projeto usava SQLite e mantinha a chave secreta no código. A chave antiga foi omitida abaixo:

SECRET_KEY = '<chave fixa omitida>'
DEBUG = True
ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

Depois, tanto os dados do PostgreSQL quanto as configurações sensíveis são lidos do ambiente:

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

.gitignore e .env.example

O .gitignore ignora .env, arquivos locais semelhantes e bancos SQLite. O .env.example versionado contém apenas nomes e valores fictícios; é usado como modelo para criar o .env real local.

Migração dos dados

Com o SQLite configurado temporariamente e o schema atualizado, os dados foram preservados por:

python manage.py migrate
python manage.py dumpdata --natural-primary --natural-foreign --exclude contenttypes --exclude auth.permission --indent 2 --output sqlite_dump.json

Depois de criar o banco, o usuário e o .env do PostgreSQL, aplique as migrações e restaure os dados:

python manage.py migrate
python manage.py loaddata sqlite_dump.json
python manage.py check
python manage.py test
python manage.py runserver

sqlite_dump.json e db.sqlite3 são ignorados pelo Git.

Validação realizada

O driver psycopg foi instalado, as migrações foram aplicadas e os dados exportados do SQLite foram carregados no PostgreSQL. O dump continha 37 objetos; a verificação posterior confirmou 5 livros.

Resultados verificados:

python manage.py check
System check identified no issues (0 silenced).

connection.vendor
postgresql

Book.objects.count()
5

As operações de cadastro, edição e exclusão ainda devem ser demonstradas nas capturas do navegador solicitadas para a entrega.

Fontes consultadas

Django, Databases: https://docs.djangoproject.com/en/5.2/ref/databases/
Django, settings DATABASES: https://docs.djangoproject.com/en/5.2/ref/settings/#databases
Django, settings SECRET_KEY: https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-SECRET_KEY
django-environ, Python environment variables: https://django-environ.readthedocs.io/en/latest/
Python Decouple: https://pypi.org/project/python-decouple/
Psycopg 3: https://www.psycopg.org/psycopg3/docs/
PostgreSQL CREATE ROLE: https://www.postgresql.org/docs/current/sql-createrole.html
PostgreSQL CREATE DATABASE: https://www.postgresql.org/docs/current/sql-createdatabase.html
