"""Widget que muestra la vista previa de una Imagen."""

import tkinter as tk

from PIL import ImageTk


class VisorImagen(tk.Canvas):
    """Lienzo que ajusta la imagen al espacio disponible.

    Hereda de tk.Canvas: reutiliza todo el comportamiento del lienzo de
    Tkinter y solo agrega lo propio del editor (escalar y centrar).
    """

    FONDO = "#2b2b2b"
    MARGEN = 10

    def __init__(self, master, **opciones):
        super().__init__(master, background=self.FONDO, highlightthickness=0, **opciones)
        self._imagen = None
        # Tkinter no guarda una referencia a la PhotoImage: si no la guardamos
        # nosotros, el recolector de basura la borra y el lienzo queda vacío.
        self._foto = None
        self.bind("<Configure>", lambda _evento: self._redibujar())
        self._mostrar_mensaje()

    def mostrar(self, imagen):
        self._imagen = imagen
        self._redibujar()

    def _mostrar_mensaje(self):
        self.delete("all")
        self.create_text(
            self.winfo_width() // 2 or 300, self.winfo_height() // 2 or 200,
            text="Abra una imagen con Archivo > Abrir (Ctrl+O)",
            fill="#bbbbbb", font=("Helvetica", 14),
        )

    def _redibujar(self):
        if self._imagen is None:
            self._mostrar_mensaje()
            return
        ancho = self.winfo_width()
        alto = self.winfo_height()
        # Antes de mostrarse la ventana el lienzo mide 1x1 px; escalar a ese
        # tamaño (menos el margen) daría un tamaño negativo y Pillow fallaría.
        if ancho <= self.MARGEN * 2 or alto <= self.MARGEN * 2:
            return
        vista = self._imagen.contenido
        vista.thumbnail((ancho - self.MARGEN * 2, alto - self.MARGEN * 2))  # solo reduce
        self._foto = ImageTk.PhotoImage(vista)
        self.delete("all")
        self.create_image(ancho // 2, alto // 2, image=self._foto, anchor="center")
