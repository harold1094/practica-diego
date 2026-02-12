import re
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout


class WordCounterWidget(QWidget):
    conteoActualizado = Signal(int, int)

    def __init__(self, wpm=200, mostrarPalabras=True, mostrarCaracteres=True, mostrarTiempoLectura=True, parent=None):
        super().__init__(parent)
        self.wpm = max(1, int(wpm))
        self.mostrarPalabras = bool(mostrarPalabras)
        self.mostrarCaracteres = bool(mostrarCaracteres)
        self.mostrarTiempoLectura = bool(mostrarTiempoLectura)

        self.lblP = QLabel("Palabras: 0")
        self.lblC = QLabel("Caracteres: 0")
        self.lblT = QLabel("Lectura: 0 min")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(6, 2, 6, 2)
        lay.setSpacing(12)
        lay.addWidget(self.lblP)
        lay.addWidget(self.lblC)
        lay.addWidget(self.lblT)
        lay.addStretch()

        self._apply_visibility()

    def _apply_visibility(self):
        self.lblP.setVisible(self.mostrarPalabras)
        self.lblC.setVisible(self.mostrarCaracteres)
        self.lblT.setVisible(self.mostrarTiempoLectura)

    def update_from_text(self, text: str):
        text = text or ""
        palabras = len(re.findall(r"\b\w+\b", text))
        caracteres = len(text)
        seg = int((palabras / self.wpm) * 60)

        self.lblP.setText(f"Palabras: {palabras}")
        self.lblC.setText(f"Caracteres: {caracteres}")
        self.lblT.setText(f"Lectura: {seg}s" if seg < 60 else f"Lectura: {round(seg/60)} min")

        self.conteoActualizado.emit(palabras, caracteres)
