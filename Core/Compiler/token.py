class Token:
    def __init__(self, type, pos, val = None):
        self._type = type
        self._val = val
        self._pos = pos

    def getType(self):
        return self._type

    def getValue(self):
        return self._val if self._val != None else self._type

    def getPosition(self):
        return self._pos

    def __str__(self) -> str:
        return f"Posição: ({str(self._pos)}), Tipo: {self._type}, Valor: {self._val}"