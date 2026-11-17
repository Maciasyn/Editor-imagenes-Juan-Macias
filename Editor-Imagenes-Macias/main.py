"""Punto de entrada: arma los objetos y abre la ventana."""

from interfaz import VentanaPrincipal
from modelos import (
    Espejo,
    FiltroBordes,
    FiltroBrillo,
    FiltroContraste,
    FiltroDesenfoque,
    FiltroGrises,
    FiltroInvertir,
    FiltroSepia,
    Rotar,
)
from servicios import CatalogoFiltros, EditorImagen


def crear_catalogo():
    """Los filtros se crean aquí y se agregan al catálogo (agregación)."""
    return CatalogoFiltros([
        FiltroGrises(),
        FiltroSepia(),
        FiltroInvertir(),
        FiltroBordes(),
        FiltroDesenfoque(),
        FiltroContraste(),
        FiltroBrillo(),
        Rotar(90),
        Rotar(270),
        Espejo(horizontal=True),
        Espejo(horizontal=False),
    ])


def main():
    ventana = VentanaPrincipal(EditorImagen(), crear_catalogo())
    ventana.mainloop()


if __name__ == "__main__":
    main()
