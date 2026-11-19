from datetime import date

from django.core.exceptions import ValidationError

def validar_ano_publicacao(valor):
    ano_atual = date.today().year 
    if valor < 1450 or valor > ano_atual:
        raise ValidationError(
            "Sistema: O ano de publicação deve estar entre 1450 e %{ano_atual}s",
            code = "ano_invalido",
            params = {"ano_atual": ano_atual},
        )






