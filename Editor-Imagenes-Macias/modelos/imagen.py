"""Modelo Imagen: envuelve una imagen de Pillow y protege su estado."""

from pathlib import Path

from PIL import Image, UnidentifiedImageError

from modelos.excepciones import ErrorImagen


class Imagen:
    """Representa una imagen del editor.

    El contenido de Pillow se guarda en un atributo no público y solo se
    entrega como copia. Así ningún objeto externo puede modificar la imagen
    "por debajo" del editor y romper el historial de deshacer.
    """

    FORMATOS_LECTURA = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")
    FORMATOS_ESCRITURA = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".bmp": "BMP"}
    MODOS_SOPORTADOS = ("RGB", "RGBA")

    def __init__(self, contenido, nombre="sin_titulo"):
        if not isinstance(contenido, Image.Image):
            raise ErrorImagen("El contenido debe ser una imagen de Pillow.")
        # Normalizamos el modo para que todos los filtros trabajen igual.
        if contenido.mode not in self.MODOS_SOPORTADOS:
            modo = "RGBA" if "A" in contenido.getbands() else "RGB"
            contenido = contenido.convert(modo)
        self.__contenido = contenido.copy()
        self.nombre = nombre

    @classmethod
    def desde_archivo(cls, ruta):
        """Crea una Imagen leyendo un archivo del disco."""
        ruta = Path(ruta)
        if not ruta.is_file():
            raise ErrorImagen(f"No se encontró el archivo: {ruta}")
        if ruta.suffix.lower() not in cls.FORMATOS_LECTURA:
            raise ErrorImagen(f"Formato no soportado: {ruta.suffix or 'sin extensión'}")
        try:
            with Image.open(ruta) as archivo:
                archivo.load()
                return cls(archivo, ruta.stem)
        except (UnidentifiedImageError, OSError) as error:
            raise ErrorImagen(f"El archivo no es una imagen válida: {ruta.name}") from error

    # Propiedades de solo lectura -------------------------------------------------

    @property
    def contenido(self):
        """Copia del contenido: modificarla no altera esta Imagen."""
        return self.__contenido.copy()

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        valor = str(valor).strip()
        if not valor:
            raise ErrorImagen("El nombre de la imagen no puede estar vacío.")
        self.__nombre = valor

    @property
    def ancho(self):
        return self.__contenido.width

    @property
    def alto(self):
        return self.__contenido.height

    @property
    def tamano(self):
        return self.__contenido.size

    @property
    def modo(self):
        return self.__contenido.mode

    # Operaciones -----------------------------------------------------------------

    def guardar(self, ruta):
        """Exporta la imagen al formato indicado por la extensión de la ruta."""
        ruta = Path(ruta)
        formato = self.FORMATOS_ESCRITURA.get(ruta.suffix.lower())
        if formato is None:
            permitidos = ", ".join(self.FORMATOS_ESCRITURA)
            raise ErrorImagen(f"Extensión no permitida para guardar. Use: {permitidos}")
        salida = self.__contenido
        # JPEG y BMP no admiten transparencia.
        if formato in ("JPEG", "BMP") and salida.mode == "RGBA":
            salida = salida.convert("RGB")
        try:
            salida.save(ruta, formato)
        except OSError as error:
            raise ErrorImagen(f"No se pudo guardar la imagen: {error}") from error
        return ruta

    def __eq__(self, otra):
        if not isinstance(otra, Imagen):
            return NotImplemented
        return self.tamano == otra.tamano and self.__contenido.tobytes() == otra.__contenido.tobytes()

    def __repr__(self):
        return f"Imagen(nombre={self.nombre!r}, tamano={self.tamano}, modo={self.modo})"
