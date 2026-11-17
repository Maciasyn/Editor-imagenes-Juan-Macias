"""Ventana principal: conecta los eventos de la interfaz con el EditorImagen."""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from modelos.excepciones import ErrorEditor
from modelos.filtros import Redimensionar
from interfaz.panel_filtros import PanelFiltros
from interfaz.visor_imagen import VisorImagen


class VentanaPrincipal(tk.Tk):
    """Administra la interfaz. No procesa imágenes: delega en el editor."""

    TIPOS_ABRIR = [("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"), ("Todos", "*.*")]
    TIPOS_GUARDAR = [("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]

    def __init__(self, editor, catalogo):
        super().__init__()
        self._editor = editor  # asociación: el editor llega construido desde main.py
        self.title("Editor de Imágenes POO")
        self.geometry("1100x700")
        self.minsize(800, 500)

        self._construir_menu()
        self._construir_barra_herramientas()

        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True)
        self._panel = PanelFiltros(cuerpo, catalogo, self._aplicar_filtro)
        self._panel.pack(side="left", fill="y")
        self._visor = VisorImagen(cuerpo)
        self._visor.pack(side="left", fill="both", expand=True)
        self._construir_historial(cuerpo)

        self._estado = tk.StringVar(value="Sin imagen")
        ttk.Label(self, textvariable=self._estado, relief="sunken", padding=4).pack(fill="x", side="bottom")

        self._atajos()
        self._actualizar()

    # Construcción ----------------------------------------------------------------

    def _construir_menu(self):
        barra = tk.Menu(self)
        archivo = tk.Menu(barra, tearoff=False)
        archivo.add_command(label="Abrir...", accelerator="Ctrl+O", command=self._abrir)
        archivo.add_command(label="Guardar como...", accelerator="Ctrl+S", command=self._guardar)
        archivo.add_separator()
        archivo.add_command(label="Salir", command=self.destroy)
        barra.add_cascade(label="Archivo", menu=archivo)

        editar = tk.Menu(barra, tearoff=False)
        editar.add_command(label="Deshacer", accelerator="Ctrl+Z", command=self._deshacer)
        editar.add_command(label="Rehacer", accelerator="Ctrl+Y", command=self._rehacer)
        editar.add_command(label="Restablecer original", command=self._restablecer)
        barra.add_cascade(label="Editar", menu=editar)

        imagen = tk.Menu(barra, tearoff=False)
        imagen.add_command(label="Redimensionar...", command=self._redimensionar)
        barra.add_cascade(label="Imagen", menu=imagen)
        self.config(menu=barra)

    def _construir_barra_herramientas(self):
        barra = ttk.Frame(self, padding=(8, 6))
        barra.pack(fill="x")
        ttk.Button(barra, text="Abrir", command=self._abrir).pack(side="left")
        self._btn_guardar = ttk.Button(barra, text="Guardar como", command=self._guardar)
        self._btn_guardar.pack(side="left", padx=4)
        ttk.Separator(barra, orient="vertical").pack(side="left", fill="y", padx=8)
        self._btn_deshacer = ttk.Button(barra, text="Deshacer", command=self._deshacer)
        self._btn_deshacer.pack(side="left")
        self._btn_rehacer = ttk.Button(barra, text="Rehacer", command=self._rehacer)
        self._btn_rehacer.pack(side="left", padx=4)
        self._btn_restablecer = ttk.Button(barra, text="Restablecer", command=self._restablecer)
        self._btn_restablecer.pack(side="left")
        self._btn_redimensionar = ttk.Button(barra, text="Redimensionar", command=self._redimensionar)
        self._btn_redimensionar.pack(side="left", padx=4)

    def _construir_historial(self, master):
        marco = ttk.Frame(master, padding=10)
        marco.pack(side="right", fill="y")
        ttk.Label(marco, text="Cambios aplicados", font=("Helvetica", 13, "bold")).pack(anchor="w")
        self._lista = tk.Listbox(marco, width=26, activestyle="none")
        self._lista.pack(fill="y", expand=True, pady=(8, 0))

    def _atajos(self):
        for secuencia, accion in (
            ("<Control-o>", self._abrir), ("<Command-o>", self._abrir),
            ("<Control-s>", self._guardar), ("<Command-s>", self._guardar),
            ("<Control-z>", self._deshacer), ("<Command-z>", self._deshacer),
            ("<Control-y>", self._rehacer), ("<Command-y>", self._rehacer),
        ):
            self.bind(secuencia, lambda _evento, a=accion: a())

    # Callbacks -------------------------------------------------------------------

    def _ejecutar(self, accion, *argumentos):
        """Ejecuta una acción del editor y muestra cualquier error previsible."""
        try:
            resultado = accion(*argumentos)
        except ErrorEditor as error:
            messagebox.showwarning("No se pudo completar", str(error), parent=self)
            return None
        self._actualizar()
        return resultado

    def _abrir(self):
        ruta = filedialog.askopenfilename(parent=self, title="Abrir imagen", filetypes=self.TIPOS_ABRIR)
        if ruta:
            self._ejecutar(self._editor.cargar, ruta)

    def _guardar(self):
        if not self._editor.tiene_imagen:
            messagebox.showinfo("Guardar", "Primero abra una imagen.", parent=self)
            return
        nombre = f"{self._editor.imagen_actual.nombre}_editada.png"
        ruta = filedialog.asksaveasfilename(
            parent=self, title="Guardar imagen", initialfile=nombre,
            defaultextension=".png", filetypes=self.TIPOS_GUARDAR,
        )
        if ruta and self._ejecutar(self._editor.guardar, ruta):
            messagebox.showinfo("Guardar", f"Imagen guardada en:\n{ruta}", parent=self)

    def _aplicar_filtro(self, filtro):
        self.configure(cursor="watch")
        self.update_idletasks()
        try:
            self._ejecutar(self._editor.aplicar, filtro)
        finally:
            self.configure(cursor="")

    def _redimensionar(self):
        if not self._editor.tiene_imagen:
            messagebox.showinfo("Redimensionar", "Primero abra una imagen.", parent=self)
            return
        actual = self._editor.imagen_actual
        ancho = simpledialog.askstring("Redimensionar", "Nuevo ancho (px):",
                                       initialvalue=str(actual.ancho), parent=self)
        if ancho is None:
            return
        alto = simpledialog.askstring("Redimensionar", "Nuevo alto (px):",
                                      initialvalue=str(actual.alto), parent=self)
        if alto is None:
            return
        try:
            filtro = Redimensionar(ancho, alto)  # valida la entrada del usuario
        except ErrorEditor as error:
            messagebox.showwarning("Valor inválido", str(error), parent=self)
            return
        self._aplicar_filtro(filtro)

    def _deshacer(self):
        self._ejecutar(self._editor.deshacer)

    def _rehacer(self):
        self._ejecutar(self._editor.rehacer)

    def _restablecer(self):
        self._ejecutar(self._editor.restablecer)

    # Refresco de la vista --------------------------------------------------------

    def _actualizar(self):
        hay = self._editor.tiene_imagen
        self._panel.habilitar(hay)
        for boton in (self._btn_guardar, self._btn_restablecer, self._btn_redimensionar):
            boton.state(["!disabled" if hay else "disabled"])
        self._btn_deshacer.state(["!disabled" if self._editor.puede_deshacer else "disabled"])
        self._btn_rehacer.state(["!disabled" if self._editor.puede_rehacer else "disabled"])

        self._lista.delete(0, "end")
        for indice, operacion in enumerate(self._editor.operaciones, start=1):
            self._lista.insert("end", f"{indice}. {operacion}")

        if hay:
            imagen = self._editor.imagen_actual
            self._visor.mostrar(imagen)
            self._estado.set(f"{imagen.nombre}  |  {imagen.ancho} x {imagen.alto} px  |  {imagen.modo}")
        else:
            self._estado.set("Sin imagen")
