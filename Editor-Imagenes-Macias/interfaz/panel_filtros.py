"""Panel lateral con un botón por cada filtro del catálogo."""

import tkinter as tk
from tkinter import ttk

from modelos.filtros import FiltroAjustable


class PanelFiltros(ttk.Frame):
    """Construye los controles a partir del catálogo.

    El panel no sabe qué hace cada filtro: solo llama al callback
    al_aplicar(filtro). Agregar un filtro nuevo al catálogo agrega su botón
    automáticamente, sin tocar este archivo.
    """

    def __init__(self, master, catalogo, al_aplicar):
        super().__init__(master, padding=10)
        self._al_aplicar = al_aplicar
        self._controles = []
        ttk.Label(self, text="Filtros y ajustes", font=("Helvetica", 13, "bold")).pack(anchor="w", pady=(0, 8))
        for filtro in catalogo:
            self._crear_control(filtro)

    def _crear_control(self, filtro):
        marco = ttk.Frame(self)
        marco.pack(fill="x", pady=3)
        boton = ttk.Button(marco, text=filtro.nombre, command=lambda: self._al_aplicar(filtro))
        boton.pack(fill="x")
        self._controles.append(boton)
        if isinstance(filtro, FiltroAjustable):
            self._crear_deslizador(marco, filtro)

    def _crear_deslizador(self, marco, filtro):
        valor = tk.DoubleVar(value=filtro.intensidad)
        etiqueta = ttk.Label(marco, text=f"Intensidad: {filtro.intensidad:.1f}")

        def al_mover(texto):
            # El setter de intensidad valida el rango.
            filtro.intensidad = round(float(texto), 1)
            etiqueta.configure(text=f"Intensidad: {filtro.intensidad:.1f}")

        deslizador = ttk.Scale(
            marco, from_=filtro.minimo, to=filtro.maximo, variable=valor, command=al_mover
        )
        deslizador.pack(fill="x")
        etiqueta.pack(anchor="w")
        self._controles.append(deslizador)

    def habilitar(self, activo):
        estado = "!disabled" if activo else "disabled"
        for control in self._controles:
            control.state([estado])
