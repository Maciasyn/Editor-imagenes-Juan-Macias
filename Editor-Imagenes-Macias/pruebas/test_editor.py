import pytest
from PIL import Image

from modelos.excepciones import ErrorEditor, ErrorImagen, SinImagenError
from modelos.filtros import FiltroGrises, FiltroInvertir, Rotar
from modelos.imagen import Imagen
from servicios.catalogo import CatalogoFiltros
from servicios.editor import EditorImagen
from servicios.historial import Historial


def test_cargar_imagen(archivo_png):
    editor = EditorImagen()
    imagen = editor.cargar(archivo_png)
    assert editor.tiene_imagen
    assert imagen.tamano == (40, 20)
    assert imagen.nombre == "foto"


def test_cargar_archivo_inexistente(tmp_path):
    with pytest.raises(ErrorImagen):
        EditorImagen().cargar(tmp_path / "no_existe.png")


def test_cargar_archivo_que_no_es_imagen(tmp_path):
    falso = tmp_path / "falso.png"
    falso.write_text("esto no es una imagen")
    with pytest.raises(ErrorImagen):
        EditorImagen().cargar(falso)


def test_aplicar_sin_imagen():
    with pytest.raises(SinImagenError):
        EditorImagen().aplicar(FiltroGrises())


def test_aplicar_algo_que_no_es_filtro(archivo_png):
    editor = EditorImagen()
    editor.cargar(archivo_png)
    with pytest.raises(ErrorEditor):
        editor.aplicar("grises")


def test_deshacer_y_rehacer(archivo_png):
    editor = EditorImagen()
    original = editor.cargar(archivo_png)
    editor.aplicar(FiltroInvertir())
    editor.aplicar(Rotar(90))
    assert editor.operaciones == ["Negativo", "Girar a la izquierda"]

    editor.deshacer()
    editor.deshacer()
    assert editor.imagen_actual == original
    assert editor.operaciones == []

    editor.rehacer()
    assert editor.operaciones == ["Negativo"]
    editor.deshacer()
    with pytest.raises(ErrorEditor):
        editor.deshacer()  # ya no quedan cambios


def test_cambio_nuevo_anula_rehacer(archivo_png):
    editor = EditorImagen()
    editor.cargar(archivo_png)
    editor.aplicar(FiltroInvertir())
    editor.deshacer()
    editor.aplicar(FiltroGrises())
    assert not editor.puede_rehacer


def test_restablecer_se_puede_deshacer(archivo_png):
    editor = EditorImagen()
    original = editor.cargar(archivo_png)
    editor.aplicar(FiltroGrises())
    editada = editor.imagen_actual
    assert editor.restablecer() == original
    assert editor.deshacer() == editada


def test_guardar_y_volver_a_abrir(tmp_path, archivo_png):
    editor = EditorImagen()
    editor.cargar(archivo_png)
    editor.aplicar(Rotar(90))
    destino = editor.guardar(tmp_path / "salida.jpg")
    assert Image.open(destino).size == (20, 40)


def test_guardar_extension_no_permitida(tmp_path, archivo_png):
    editor = EditorImagen()
    editor.cargar(archivo_png)
    with pytest.raises(ErrorImagen):
        editor.guardar(tmp_path / "salida.txt")


def test_contenido_es_copia(imagen_color):
    copia = imagen_color.contenido
    copia.putpixel((0, 0), (0, 0, 0))
    assert imagen_color.contenido.getpixel((0, 0)) == (255, 0, 0)


def test_imagen_rechaza_contenido_invalido():
    with pytest.raises(ErrorImagen):
        Imagen("no soy una imagen")


def test_historial_respeta_limite():
    historial = Historial(limite=2)
    for estado in ("a", "b", "c"):
        historial.registrar(estado)
    assert historial.cantidad == 2
    assert historial.deshacer("d") == "c"
    assert historial.deshacer("c") == "b"
    assert historial.deshacer("b") is None


def test_catalogo_rechaza_duplicados_y_no_filtros():
    catalogo = CatalogoFiltros([FiltroGrises()])
    with pytest.raises(ValueError):
        catalogo.registrar(FiltroGrises())
    with pytest.raises(TypeError):
        catalogo.registrar("grises")
    assert catalogo.obtener("Escala de grises").nombre == "Escala de grises"
