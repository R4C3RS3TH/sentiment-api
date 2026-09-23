"""Funciones de validación y preprocesamiento de texto de entrada."""
import re

MAX_TEXT_LENGTH = 1000


class InvalidTextError(ValueError):
    """Se lanza cuando el texto de entrada no es válido para clasificar."""


def clean_text(text: str) -> str:
    """Normaliza espacios en blanco y recorta el texto."""
    if text is None:
        raise InvalidTextError("El texto no puede ser None")
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned


def validate_text(text: str) -> str:
    """Valida y limpia el texto de entrada.

    Lanza InvalidTextError si el texto está vacío, no es string
    o excede la longitud máxima permitida.
    """
    if not isinstance(text, str):
        raise InvalidTextError("El texto debe ser una cadena de caracteres")

    cleaned = clean_text(text)

    if len(cleaned) == 0:
        raise InvalidTextError("El texto no puede estar vacío")

    if len(cleaned) > MAX_TEXT_LENGTH:
        raise InvalidTextError(
            f"El texto excede la longitud máxima de {MAX_TEXT_LENGTH} caracteres"
        )

    return cleaned
