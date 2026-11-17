"""Entidades del dominio: la imagen, los filtros y los errores."""

from modelos.excepciones import ErrorEditor, ErrorImagen, ErrorParametro, SinImagenError
from modelos.filtros import (
    Espejo,
    Filtro,
    FiltroAjustable,
    FiltroBordes,
    FiltroBrillo,
    FiltroContraste,
    FiltroDesenfoque,
    FiltroGrises,
    FiltroInvertir,
    FiltroSepia,
    Redimensionar,
    Rotar,
)
from modelos.imagen import Imagen

__all__ = [
    "ErrorEditor", "ErrorImagen", "ErrorParametro", "SinImagenError",
    "Imagen", "Filtro", "FiltroAjustable", "FiltroGrises", "FiltroSepia",
    "FiltroInvertir", "FiltroBordes", "FiltroDesenfoque", "FiltroContraste",
    "FiltroBrillo", "Rotar", "Espejo", "Redimensionar",
]
