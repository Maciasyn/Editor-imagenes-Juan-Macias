"""Lógica principal de la aplicación: coordina imagen, filtros e historial."""

from modelos.excepciones import ErrorEditor, SinImagenError
from modelos.filtros import Filtro
from modelos.imagen import Imagen
from servicios.historial import Historial


class EditorImagen:
    """Coordina las operaciones del usuario sobre una imagen.

    1. Composición con Historial: el editor crea su propio historial y este
       no tiene sentido fuera del editor.
    2. Asociación con Filtro: el editor usa un filtro durante aplicar(),
       pero no lo guarda ni lo crea.
    3. La interfaz nunca toca Pillow directamente; todo pasa por aquí.
    """

    def __init__(self, limite_historial=20):
        self._historial = Historial(limite_historial)
        self._original = None
        self._actual = None
        self._operaciones = []

    # Consultas -------------------------------------------------------------------

    @property
    def tiene_imagen(self):
        return self._actual is not None

    @property
    def imagen_actual(self):
        return self._actual

    @property
    def operaciones(self):
        """Lista (copia) de los nombres de filtros aplicados, en orden."""
        return list(self._operaciones)

    @property
    def puede_deshacer(self):
        return self._historial.puede_deshacer

    @property
    def puede_rehacer(self):
        return self._historial.puede_rehacer

    def _exigir_imagen(self):
        if not self.tiene_imagen:
            raise SinImagenError("Primero abra una imagen.")

    # Operaciones -----------------------------------------------------------------

    def cargar(self, ruta):
        imagen = Imagen.desde_archivo(ruta)
        self._original = imagen
        self._actual = imagen
        self._historial.limpiar()
        self._operaciones.clear()
        return imagen

    def aplicar(self, filtro):
        """Aplica cualquier Filtro. Aquí ocurre el polimorfismo."""
        self._exigir_imagen()
        if not isinstance(filtro, Filtro):
            raise ErrorEditor("La operación solicitada no es un filtro válido.")
        resultado = filtro.aplicar(self._actual)
        self._historial.registrar((self._actual, list(self._operaciones)))
        self._actual = resultado
        self._operaciones.append(str(filtro))
        return resultado

    def deshacer(self):
        self._exigir_imagen()
        previo = self._historial.deshacer((self._actual, list(self._operaciones)))
        if previo is None:
            raise ErrorEditor("No hay cambios para deshacer.")
        self._actual, self._operaciones = previo
        return self._actual

    def rehacer(self):
        self._exigir_imagen()
        siguiente = self._historial.rehacer((self._actual, list(self._operaciones)))
        if siguiente is None:
            raise ErrorEditor("No hay cambios para rehacer.")
        self._actual, self._operaciones = siguiente
        return self._actual

    def restablecer(self):
        """Vuelve a la imagen original. Se puede deshacer."""
        self._exigir_imagen()
        if self._actual is self._original:
            return self._actual
        self._historial.registrar((self._actual, list(self._operaciones)))
        self._actual = self._original
        self._operaciones = []
        return self._actual

    def guardar(self, ruta):
        self._exigir_imagen()
        return self._actual.guardar(ruta)
