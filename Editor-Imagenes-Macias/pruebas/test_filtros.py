import pytest

from modelos.excepciones import ErrorParametro
from modelos.filtros import (
    Espejo,
    Filtro,
    FiltroBrillo,
    FiltroContraste,
    FiltroDesenfoque,
    FiltroGrises,
    FiltroInvertir,
    FiltroSepia,
    Redimensionar,
    Rotar,
)


def test_filtro_es_abstracto():
    with pytest.raises(TypeError):
        Filtro("x")


def test_grises_deja_canales_iguales(imagen_color):
    resultado = FiltroGrises().aplicar(imagen_color)
    r, g, b = resultado.contenido.getpixel((0, 0))
    assert r == g == b


def test_aplicar_no_modifica_la_original(imagen_color):
    antes = imagen_color.contenido.getpixel((0, 0))
    FiltroInvertir().aplicar(imagen_color)
    assert imagen_color.contenido.getpixel((0, 0)) == antes


def test_invertir_rojo_da_cian(imagen_color):
    assert FiltroInvertir().aplicar(imagen_color).contenido.getpixel((0, 0)) == (0, 255, 255)


def test_polimorfismo_misma_llamada_distinto_resultado(imagen_color):
    filtros = [FiltroGrises(), FiltroSepia(), FiltroInvertir(), FiltroBrillo(2.0)]
    pixeles = {f.aplicar(imagen_color).contenido.getpixel((0, 0)) for f in filtros}
    assert len(pixeles) == len(filtros)


def test_rotar_intercambia_dimensiones(imagen_color):
    assert Rotar(90).aplicar(imagen_color).tamano == (20, 40)


def test_rotar_angulo_invalido():
    with pytest.raises(ErrorParametro):
        Rotar(45)


def test_espejo_horizontal(imagen_color):
    assert Espejo().aplicar(imagen_color).contenido.getpixel((0, 0)) == (0, 0, 255)


def test_redimensionar(imagen_color):
    assert Redimensionar("80", 10).aplicar(imagen_color).tamano == (80, 10)


@pytest.mark.parametrize("ancho, alto", [("abc", 10), (0, 10), (10, -5), (9000, 10)])
def test_redimensionar_entradas_invalidas(ancho, alto):
    with pytest.raises(ErrorParametro):
        Redimensionar(ancho, alto)


@pytest.mark.parametrize("clase", [FiltroDesenfoque, FiltroContraste, FiltroBrillo])
def test_intensidad_fuera_de_rango(clase):
    filtro = clase()
    with pytest.raises(ErrorParametro):
        filtro.intensidad = 99
    with pytest.raises(ErrorParametro):
        filtro.intensidad = "mucho"


def test_intensidad_valida_se_guarda():
    filtro = FiltroContraste()
    filtro.intensidad = 2.5
    assert filtro.intensidad == 2.5
    assert str(filtro) == "Contraste (2.5)"
