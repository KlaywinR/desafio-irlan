from django.core.exceptions import ValidationError
from django.utils import timezone


def validar_ano_publicacao(ano):
    ano_atual = timezone.localdate().year
    if ano < 1450 or ano > ano_atual:
        raise ValidationError(
            "O ano de publicação deve estar entre 1450 e %(ano_atual)s.",
            code="ano_invalido",
            params={"ano_atual": ano_atual},
        )

