"""Historial de estados para deshacer y rehacer."""


class Historial:
    """Guarda estados anteriores y posteriores con un límite de memoria.

    Las pilas son no públicas: solo se modifican con registrar(), deshacer()
    y rehacer(), de modo que el orden de los estados siempre es coherente.
    """

    def __init__(self, limite=20):
        if limite < 1:
            raise ValueError("El límite del historial debe ser al menos 1.")
        self._limite = limite
        self._anteriores = []
        self._siguientes = []

    @property
    def puede_deshacer(self):
        return bool(self._anteriores)

    @property
    def puede_rehacer(self):
        return bool(self._siguientes)

    @property
    def cantidad(self):
        return len(self._anteriores)

    def registrar(self, estado):
        """Guarda el estado previo a un cambio. Un cambio nuevo anula el rehacer."""
        self._anteriores.append(estado)
        if len(self._anteriores) > self._limite:
            self._anteriores.pop(0)  # se descarta el estado más antiguo
        self._siguientes.clear()

    def deshacer(self, estado_actual):
        if not self._anteriores:
            return None
        self._siguientes.append(estado_actual)
        return self._anteriores.pop()

    def rehacer(self, estado_actual):
        if not self._siguientes:
            return None
        self._anteriores.append(estado_actual)
        return self._siguientes.pop()

    def limpiar(self):
        self._anteriores.clear()
        self._siguientes.clear()
