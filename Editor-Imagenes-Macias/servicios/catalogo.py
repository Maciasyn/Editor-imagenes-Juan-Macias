"""Catálogo de filtros disponibles en la interfaz."""

from modelos.filtros import Filtro


class CatalogoFiltros:
    """Agrupa filtros creados fuera de él (agregación).

    El catálogo no crea los filtros ni controla su ciclo de vida: los recibe
    ya construidos. Si el catálogo desaparece, los filtros pueden seguir
    usándose en otra parte.
    """

    def __init__(self, filtros=None):
        self._filtros = {}
        for filtro in filtros or []:
            self.registrar(filtro)

    def registrar(self, filtro):
        if not isinstance(filtro, Filtro):
            raise TypeError("Solo se pueden registrar objetos de tipo Filtro.")
        if filtro.nombre in self._filtros:
            raise ValueError(f"Ya existe un filtro llamado {filtro.nombre!r}.")
        self._filtros[filtro.nombre] = filtro

    def obtener(self, nombre):
        try:
            return self._filtros[nombre]
        except KeyError:
            raise KeyError(f"No existe el filtro {nombre!r}.") from None

    @property
    def filtros(self):
        return list(self._filtros.values())

    def __len__(self):
        return len(self._filtros)

    def __iter__(self):
        return iter(self.filtros)
