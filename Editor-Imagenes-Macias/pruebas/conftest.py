import pytest
from PIL import Image

from modelos.imagen import Imagen


@pytest.fixture
def imagen_color():
    """Imagen RGB de 40x20: mitad roja y mitad azul."""
    pil = Image.new("RGB", (40, 20), "red")
    pil.paste(Image.new("RGB", (20, 20), "blue"), (20, 0))
    return Imagen(pil, "prueba")


@pytest.fixture
def archivo_png(tmp_path, imagen_color):
    ruta = tmp_path / "foto.png"
    imagen_color.guardar(ruta)
    return ruta
