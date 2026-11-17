"""Jerarquía de filtros.

Filtro es una clase abstracta: define el contrato "toda operación sobre una
imagen recibe una Imagen y devuelve una Imagen nueva". Cada subclase decide
cómo transformar los píxeles en el método procesar().
"""

from abc import ABC, abstractmethod

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from modelos.excepciones import ErrorParametro
from modelos.imagen import Imagen


class Filtro(ABC):
    """Contrato común para todas las operaciones del editor."""

    def __init__(self, nombre, descripcion=""):
        self._nombre = nombre
        self._descripcion = descripcion

    @property
    def nombre(self):
        return self._nombre

    @property
    def descripcion(self):
        return self._descripcion

    def aplicar(self, imagen):
        """Aplica el filtro sin modificar la imagen original.

        Es un método plantilla: el flujo es el mismo para todos los filtros
        y solo cambia procesar(), que cada subclase implementa a su manera.
        """
        if not isinstance(imagen, Imagen):
            raise TypeError("aplicar() espera un objeto Imagen.")
        resultado = self.procesar(imagen.contenido)
        return Imagen(resultado, imagen.nombre)

    @abstractmethod
    def procesar(self, pil_imagen):
        """Recibe una imagen de Pillow y devuelve otra transformada."""

    def __str__(self):
        return self.nombre


# Utilidad para filtros que no deben tocar el canal de transparencia ----------------

def _sobre_rgb(pil_imagen, transformacion):
    """Aplica una transformación a los canales RGB y conserva el alfa."""
    if pil_imagen.mode == "RGBA":
        alfa = pil_imagen.getchannel("A")
        rgb = transformacion(pil_imagen.convert("RGB"))
        rgb.putalpha(alfa)
        return rgb
    return transformacion(pil_imagen)


# Filtros simples (sin parámetros) ----------------------------------------------------

class FiltroGrises(Filtro):
    def __init__(self):
        super().__init__("Escala de grises", "Convierte la imagen a tonos de gris.")

    def procesar(self, pil_imagen):
        return _sobre_rgb(pil_imagen, lambda rgb: ImageOps.grayscale(rgb).convert("RGB"))


class FiltroSepia(Filtro):
    def __init__(self):
        super().__init__("Sepia", "Da un tono cálido de fotografía antigua.")

    def procesar(self, pil_imagen):
        def sepia(rgb):
            gris = ImageOps.grayscale(rgb)
            return ImageOps.colorize(gris, black="#2e1f0f", white="#f5e6c8")
        return _sobre_rgb(pil_imagen, sepia)


class FiltroInvertir(Filtro):
    def __init__(self):
        super().__init__("Negativo", "Invierte los colores de la imagen.")

    def procesar(self, pil_imagen):
        return _sobre_rgb(pil_imagen, ImageOps.invert)


class FiltroBordes(Filtro):
    def __init__(self):
        super().__init__("Detectar bordes", "Resalta los contornos de la imagen.")

    def procesar(self, pil_imagen):
        return _sobre_rgb(pil_imagen, lambda rgb: rgb.filter(ImageFilter.FIND_EDGES))


# Filtros ajustables (con intensidad validada) -----------------------------------

class FiltroAjustable(Filtro):
    """Filtro con una intensidad que debe estar dentro de un rango.

    Reúne la validación en un solo lugar: las subclases solo declaran su
    rango y su valor por defecto mediante super().__init__().
    """

    def __init__(self, nombre, descripcion, minimo, maximo, valor_inicial):
        super().__init__(nombre, descripcion)
        if minimo >= maximo:
            raise ErrorParametro("El mínimo debe ser menor que el máximo.")
        self._minimo = minimo
        self._maximo = maximo
        self.intensidad = valor_inicial  # pasa por el setter y se valida

    @property
    def minimo(self):
        return self._minimo

    @property
    def maximo(self):
        return self._maximo

    @property
    def intensidad(self):
        return self._intensidad

    @intensidad.setter
    def intensidad(self, valor):
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            raise ErrorParametro(f"La intensidad de {self.nombre} debe ser un número.") from None
        if not self._minimo <= valor <= self._maximo:
            raise ErrorParametro(
                f"La intensidad de {self.nombre} debe estar entre {self._minimo} y {self._maximo}."
            )
        self._intensidad = valor

    def __str__(self):
        return f"{self.nombre} ({self.intensidad:g})"


class FiltroDesenfoque(FiltroAjustable):
    def __init__(self, radio=2.0):
        super().__init__("Desenfoque", "Suaviza la imagen (desenfoque gaussiano).", 0.5, 15.0, radio)

    def procesar(self, pil_imagen):
        return pil_imagen.filter(ImageFilter.GaussianBlur(self.intensidad))


class FiltroContraste(FiltroAjustable):
    def __init__(self, factor=1.5):
        super().__init__("Contraste", "Aumenta o reduce la diferencia entre tonos.", 0.1, 3.0, factor)

    def procesar(self, pil_imagen):
        return _sobre_rgb(pil_imagen, lambda rgb: ImageEnhance.Contrast(rgb).enhance(self.intensidad))


class FiltroBrillo(FiltroAjustable):
    def __init__(self, factor=1.3):
        super().__init__("Brillo", "Aclara u oscurece la imagen.", 0.1, 3.0, factor)

    def procesar(self, pil_imagen):
        return _sobre_rgb(pil_imagen, lambda rgb: ImageEnhance.Brightness(rgb).enhance(self.intensidad))


# Transformaciones geométricas --------------------------------------------------------

class Rotar(Filtro):
    ANGULOS_VALIDOS = (90, 180, 270)

    def __init__(self, grados=90):
        if grados not in self.ANGULOS_VALIDOS:
            raise ErrorParametro("Solo se puede rotar 90, 180 o 270 grados.")
        # Pillow gira en sentido antihorario: 90 es a la izquierda, 270 a la derecha.
        nombres = {90: "Girar a la izquierda", 180: "Girar 180°", 270: "Girar a la derecha"}
        super().__init__(nombres[grados], "Gira la imagen sin recortarla.")
        self._grados = grados

    def procesar(self, pil_imagen):
        return pil_imagen.rotate(self._grados, expand=True)


class Espejo(Filtro):
    def __init__(self, horizontal=True):
        nombre = "Espejo horizontal" if horizontal else "Espejo vertical"
        super().__init__(nombre, "Refleja la imagen.")
        self._horizontal = horizontal

    def procesar(self, pil_imagen):
        return ImageOps.mirror(pil_imagen) if self._horizontal else ImageOps.flip(pil_imagen)


class Redimensionar(Filtro):
    LADO_MAXIMO = 8000

    def __init__(self, ancho, alto):
        super().__init__("Redimensionar", "Cambia el tamaño en píxeles.")
        self._ancho = self._validar_lado(ancho, "ancho")
        self._alto = self._validar_lado(alto, "alto")
        self._nombre = f"Redimensionar a {self._ancho}x{self._alto}"

    def _validar_lado(self, valor, etiqueta):
        try:
            valor = int(str(valor).strip())
        except ValueError:
            raise ErrorParametro(f"El {etiqueta} debe ser un número entero.") from None
        if not 1 <= valor <= self.LADO_MAXIMO:
            raise ErrorParametro(f"El {etiqueta} debe estar entre 1 y {self.LADO_MAXIMO} píxeles.")
        return valor

    def procesar(self, pil_imagen):
        return pil_imagen.resize((self._ancho, self._alto), Image.LANCZOS)
