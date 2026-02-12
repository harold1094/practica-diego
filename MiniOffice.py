import os
import speech_recognition as sr
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QAction, QKeySequence, QIcon, QTextDocument, QTextCursor, QTextCharFormat
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QToolBar, QStatusBar, QLabel,
    QFileDialog, QColorDialog, QFontDialog, QMenu,
    QMessageBox,
    QDockWidget, QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout
)
from word_counter_widget import WordCounterWidget


class VoiceWorker(QThread):
    recognized = Signal(str)
    status = Signal(str)

    def __init__(self, language="es-ES", parent=None):
        super().__init__(parent)
        self.language = language
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        r = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                self.status.emit("🎤 Calibrando ruido…")
                r.adjust_for_ambient_noise(source, duration=0.6)
                if not self._running:
                    return
                self.status.emit("🎧 Escuchando… (habla ahora)")
                audio = r.listen(source, phrase_time_limit=5)
            if not self._running:
                return
            self.status.emit("🧠 Transcribiendo…")
            text = r.recognize_google(audio, language=self.language)
            self.recognized.emit(text)
        except sr.UnknownValueError:
            self.status.emit("No te he entendido 😅 (prueba otra vez)")
        except sr.RequestError as e:
            self.status.emit(f"Error con el servicio de reconocimiento: {e}")
        except Exception as e:
            self.status.emit(f"Error de micro/audio: {e}")


class MiniOffice(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Word - Harold Ríos Gallego")
        self.resize(900, 600)

        self.editor = QTextEdit(self)
        self.setCentralWidget(self.editor)

        self.setStatusBar(QStatusBar())
        self.word_counter = WordCounterWidget(wpm=200, mostrarPalabras=True, mostrarCaracteres=True, mostrarTiempoLectura=True, parent=self)
        self.statusBar().addPermanentWidget(self.word_counter)
        self.word_counter.conteoActualizado.connect(self.on_conteo_actualizado)
        self.statusBar().showMessage("Desarrollado por Harold Ríos Gallego")
        self.barra_estado = self.statusBar()

        self.timer_palabras = QTimer(self)
        self.timer_palabras.setInterval(200)
        self.timer_palabras.setSingleShot(True)
        self.timer_palabras.timeout.connect(self.actualizar_contador_palabras)
        self.editor.textChanged.connect(self.reiniciar_temporizador_palabras)

        self.ruta_actual = None

        barra_menus = self.menuBar()
        menu_archivo: QMenu = barra_menus.addMenu("&Archivo")
        menu_editar: QMenu = barra_menus.addMenu("&Editar")
        menu_formato: QMenu = barra_menus.addMenu("&Formato")

        self.act_nuevo = QAction("Nuevo", self)
        self.act_abrir = QAction("Abrir…", self)
        self.act_guardar = QAction("Guardar", self)
        self.act_salir = QAction("Salir", self)

        self.act_nuevo.setShortcut(QKeySequence("Ctrl+N"))
        self.act_abrir.setShortcut(QKeySequence("Ctrl+O"))
        self.act_guardar.setShortcut(QKeySequence("Ctrl+S"))
        self.act_salir.setShortcut(QKeySequence("Ctrl+Q"))

        self.act_deshacer = QAction("Deshacer", self)
        self.act_rehacer = QAction("Rehacer", self)
        self.act_cortar = QAction("Cortar", self)
        self.act_copiar = QAction("Copiar", self)
        self.act_pegar = QAction("Pegar", self)
        self.act_buscar = QAction("Buscar…", self)
        self.act_reempl = QAction("Reemplazar…", self)

        self.act_deshacer.setShortcut(QKeySequence("Ctrl+Z"))
        self.act_rehacer.setShortcut(QKeySequence("Ctrl+Y"))
        self.act_cortar.setShortcut(QKeySequence("Ctrl+X"))
        self.act_copiar.setShortcut(QKeySequence("Ctrl+C"))
        self.act_pegar.setShortcut(QKeySequence("Ctrl+V"))
        self.act_buscar.setShortcut(QKeySequence("Ctrl+F"))
        self.act_reempl.setShortcut(QKeySequence("Ctrl+H"))

        self.act_color_fondo = QAction("Color de fondo…", self)
        self.act_fuente = QAction("Tipo de letra…", self)

        base = os.path.dirname(__file__)

        def set_icon(act, name):
            ruta = os.path.join(base, "icons", name)
            if os.path.exists(ruta):
                act.setIcon(QIcon(ruta))

        set_icon(self.act_nuevo,   "new.png")
        set_icon(self.act_abrir,   "open.png")
        set_icon(self.act_guardar, "save.png")
        set_icon(self.act_deshacer, "undo.png")
        set_icon(self.act_rehacer, "redo.png")
        set_icon(self.act_cortar,  "cut.png")
        set_icon(self.act_copiar,  "copy.png")
        set_icon(self.act_pegar,   "paste.png")
        set_icon(self.act_buscar,  "find.png")
        set_icon(self.act_reempl,  "replace.png")

        self.act_nuevo.triggered.connect(self.accion_nuevo)
        self.act_abrir.triggered.connect(self.accion_abrir)
        self.act_guardar.triggered.connect(self.accion_guardar)
        self.act_salir.triggered.connect(self.close)

        self.act_deshacer.triggered.connect(self.editor.undo)
        self.act_rehacer.triggered.connect(self.editor.redo)
        self.act_cortar.triggered.connect(self.editor.cut)
        self.act_copiar.triggered.connect(self.editor.copy)
        self.act_pegar.triggered.connect(self.editor.paste)
        self.act_buscar.triggered.connect(self.accion_buscar)
        self.act_reempl.triggered.connect(self.accion_reemplazar)

        self.act_color_fondo.triggered.connect(self.accion_color_fondo)
        self.act_fuente.triggered.connect(self.accion_fuente)

        menu_archivo.addAction(self.act_nuevo)
        menu_archivo.addAction(self.act_abrir)
        menu_archivo.addAction(self.act_guardar)
        menu_archivo.addSeparator()
        menu_archivo.addAction(self.act_salir)

        menu_editar.addAction(self.act_deshacer)
        menu_editar.addAction(self.act_rehacer)
        menu_editar.addSeparator()
        menu_editar.addAction(self.act_cortar)
        menu_editar.addAction(self.act_copiar)
        menu_editar.addAction(self.act_pegar)
        menu_editar.addSeparator()
        menu_editar.addAction(self.act_buscar)
        menu_editar.addAction(self.act_reempl)

        menu_formato.addAction(self.act_color_fondo)
        menu_formato.addAction(self.act_fuente)

        barra_herr = QToolBar("Acciones", self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, barra_herr)
        barra_herr.setMovable(True)

        for act in [
            self.act_nuevo, self.act_abrir, self.act_guardar,
            self.act_deshacer, self.act_rehacer,
            self.act_cortar, self.act_copiar, self.act_pegar,
            self.act_buscar, self.act_reempl
        ]:
            barra_herr.addAction(act)

        # --- VOZ (Dictado) ---
        self.voice_worker = None
        self.act_voz = QAction("Dictado (🎤)", self)
        self.act_parar_voz = QAction("Parar dictado", self)
        self.act_voz.setShortcut(QKeySequence("Ctrl+M"))
        self.act_voz.triggered.connect(self.accion_dictado)
        self.act_parar_voz.triggered.connect(self.accion_parar_dictado)
        barra_herr.addSeparator()
        barra_herr.addAction(self.act_voz)
        barra_herr.addAction(self.act_parar_voz)

        self.dock_buscar = QDockWidget("Buscar", self)
        panel_buscar = QWidget(self.dock_buscar)

        self.input_buscar = QLineEdit(panel_buscar)
        self.input_buscar.setPlaceholderText("Texto a buscar...")

        btn_abajo = QPushButton("Buscar abajo", panel_buscar)
        btn_arriba = QPushButton("Buscar arriba", panel_buscar)
        btn_todas = QPushButton("Buscar todas", panel_buscar)

        layout_botones = QHBoxLayout()
        layout_botones.addWidget(btn_abajo)
        layout_botones.addWidget(btn_arriba)

        layout_panel = QVBoxLayout(panel_buscar)
        layout_panel.addWidget(QLabel("Buscar:", panel_buscar))
        layout_panel.addWidget(self.input_buscar)
        layout_panel.addLayout(layout_botones)
        layout_panel.addWidget(btn_todas)

        panel_buscar.setLayout(layout_panel)
        self.dock_buscar.setWidget(panel_buscar)

        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_buscar)
        self.dock_buscar.hide()

        btn_abajo.clicked.connect(lambda: self.buscar_texto_panel(hacia_arriba=False))
        btn_arriba.clicked.connect(lambda: self.buscar_texto_panel(hacia_arriba=True))
        btn_todas.clicked.connect(self.buscar_todas)


    def accion_nuevo(self):
        self.editor.clear()
        self.ruta_actual = None
        self.barra_estado.showMessage("Nuevo documento", 3000)
        self.actualizar_contador_palabras()

    def accion_abrir(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir archivo",
            "",
            "Texto (*.txt);;Todos (*.*)"
        )
        if ruta:
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    contenido = f.read()
                self.editor.setPlainText(contenido)
                self.ruta_actual = ruta
                self.barra_estado.showMessage(
                    f"Archivo abierto: {os.path.basename(ruta)}", 3000
                )
                self.actualizar_contador_palabras()
            except Exception as e:
                self.barra_estado.showMessage(f"Error al abrir: {e}", 5000)

    def accion_guardar(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar archivo",
            "",
            "Archivos de texto (*.txt)"
        )
        if ruta:
            try:
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(self.editor.toPlainText())
                mensaje = f"Archivo guardado en: {ruta}"
                self.barra_estado.showMessage(mensaje)
                QMessageBox.information(self, "Guardar", mensaje)
            except Exception as e:
                mensaje_error = f"No se pudo guardar el archivo: {str(e)}"
                QMessageBox.warning(self, "Error", mensaje_error)
                self.barra_estado.showMessage(mensaje_error)


    def accion_buscar(self):
        self.dock_buscar.show()
        self.dock_buscar.raise_()
        self.input_buscar.setFocus()
        self.input_buscar.selectAll()
        self.barra_estado.showMessage("Panel de búsqueda abierto", 2000)

    def accion_reemplazar(self):
        self.dock_buscar.show()
        self.dock_buscar.raise_()
        self.input_buscar.setFocus()
        self.input_buscar.selectAll()
        self.barra_estado.showMessage("Panel de búsqueda (reemplazar pendiente)", 2000)

    def buscar_texto_panel(self, hacia_arriba=False):
        texto_buscado = self.input_buscar.text()
        if not texto_buscado:
            QMessageBox.information(self, "Buscar", "Por favor, ingresa texto para buscar.")
            return

        if hacia_arriba:
            encontrado = self.editor.find(
                texto_buscado,
                QTextDocument.FindFlag.FindBackward
            )
        else:
            encontrado = self.editor.find(texto_buscado)

        if not encontrado:
            mensaje = f"No se encontró: {texto_buscado}"
            QMessageBox.information(self, "Buscar", mensaje)
            self.barra_estado.showMessage(mensaje)
        else:
            self.barra_estado.showMessage(f"Texto encontrado: {texto_buscado}")

    def buscar_todas(self):
        texto_buscado = self.input_buscar.text()
        if not texto_buscado:
            QMessageBox.information(self, "Buscar todas", "Por favor, ingresa texto para buscar.")
            return

        doc = self.editor.document()
        cursor = QTextCursor(doc)
        flags = QTextDocument.FindFlag(0)

        selecciones = []
        coincidencias = 0

        while True:
            cursor = doc.find(texto_buscado, cursor, flags)
            if cursor.isNull():
                break

            extra = QTextEdit.ExtraSelection()
            formato = QTextCharFormat()
            formato.setBackground(Qt.yellow)
            extra.cursor = cursor
            extra.format = formato

            selecciones.append(extra)
            coincidencias += 1

        self.editor.setExtraSelections(selecciones)

        if coincidencias == 0:
            mensaje = f"No se encontraron coincidencias para: {texto_buscado}"
            QMessageBox.information(self, "Buscar todas", mensaje)
            self.barra_estado.showMessage(mensaje)
        else:
            self.barra_estado.showMessage(f"Coincidencias encontradas: {coincidencias}")


    def accion_color_fondo(self):
        color = QColorDialog.getColor(
            self.editor.palette().base().color(), self, "Color de fondo"
        )
        if color.isValid():
            pal = self.editor.palette()
            pal.setColor(self.editor.viewport().backgroundRole(), color)
            self.editor.viewport().setPalette(pal)
            self.editor.viewport().setAutoFillBackground(True)
            self.barra_estado.showMessage("Color de fondo actualizado", 2000)

    def accion_fuente(self):
        ok, fuente = QFontDialog.getFont(self.editor.font(), self, "Tipo de letra")
        if ok:
            self.editor.setFont(fuente)
            self.barra_estado.showMessage("Fuente actualizada", 2000)


    def reiniciar_temporizador_palabras(self):
        self.timer_palabras.start()

    # ---------------- VOZ ----------------
    def accion_dictado(self):
        if self.voice_worker and self.voice_worker.isRunning():
            self.barra_estado.showMessage("Ya estoy escuchando 😄", 2000)
            return

        self.voice_worker = VoiceWorker(language="es-ES", parent=self)
        self.voice_worker.status.connect(lambda msg: self.barra_estado.showMessage(msg, 4000))
        self.voice_worker.recognized.connect(self.procesar_texto_voz)
        self.voice_worker.start()

    def accion_parar_dictado(self):
        if self.voice_worker and self.voice_worker.isRunning():
            self.voice_worker.stop()
            self.barra_estado.showMessage("Dictado detenido", 2000)
        else:
            self.barra_estado.showMessage("No había dictado activo", 2000)

    def procesar_texto_voz(self, texto: str):
        t = (texto or "").strip()
        if not t:
            return

        comando = t.lower()

        # Comandos por voz
        if "negrita" in comando:
            self.toggle_negrita()
            self.barra_estado.showMessage("✅ Negrita", 2000)
            return
        if "cursiva" in comando:
            self.toggle_cursiva()
            self.barra_estado.showMessage("✅ Cursiva", 2000)
            return
        if "subrayado" in comando:
            self.toggle_subrayado()
            self.barra_estado.showMessage("✅ Subrayado", 2000)
            return
        if "guardar archivo" in comando or comando == "guardar":
            self.accion_guardar()
            return
        if "nuevo documento" in comando or comando == "nuevo":
            self.accion_nuevo()
            return

        # Si no es comando → insertar texto
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()
        cursor.insertText(t + " ")
        self.editor.setTextCursor(cursor)
        self.barra_estado.showMessage(f"📝 Dictado: {t}", 3000)

    def _merge_format_on_selection(self, fmt: QTextCharFormat):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            self.editor.setTextCursor(cursor)
        cursor.mergeCharFormat(fmt)
        self.editor.mergeCurrentCharFormat(fmt)

    def toggle_negrita(self):
        fmt = QTextCharFormat()
        current = self.editor.fontWeight()
        fmt.setFontWeight(400 if current > 400 else 700)
        self._merge_format_on_selection(fmt)

    def toggle_cursiva(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.editor.fontItalic())
        self._merge_format_on_selection(fmt)

    def toggle_subrayado(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not self.editor.fontUnderline())
        self._merge_format_on_selection(fmt)

    def actualizar_contador_palabras(self):
        texto = self.editor.toPlainText()
        self.word_counter.update_from_text(texto)

    def on_conteo_actualizado(self, palabras, caracteres):
        self.barra_estado.showMessage(f"Palabras: {palabras} | Caracteres: {caracteres}", 3000)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = MiniOffice()
    win.show()
    sys.exit(app.exec())
