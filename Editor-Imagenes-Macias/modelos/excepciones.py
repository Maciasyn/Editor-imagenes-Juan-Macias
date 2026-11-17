"""Excepciones propias del editor.

Tener una jerarquía propia permite que la interfaz capture un solo tipo
(ErrorEditor) y muestre un mensaje claro, sin conocer los detalles internos.
"""


class ErrorEditor(Exception):
    """Clase base de todos los errores previsibles de la aplicación."""


class ErrorImagen(ErrorEditor):
    """La imagen no existe, no se puede leer o tiene un formato no soportado."""


class ErrorParametro(ErrorEditor):
    """Un filtro recibió un valor fuera de su rango permitido."""


class SinImagenError(ErrorEditor):
    """Se intentó una operación sin haber cargado una imagen."""
