# MiniOffice

Proyecto de la asignatura **Desarrollo de Interfaces**.

## Descripción general

MiniOffice es una aplicación de escritorio hecha en **Python y PySide6** que funciona como un pequeño editor de texto. Permite crear, abrir, editar y guardar documentos de texto desde una interfaz gráfica sencilla y clara.

## Funcionalidades principales

- Crear documentos nuevos y guardar cambios en archivos de texto.
- Abrir archivos de texto existentes desde un cuadro de diálogo.
- Función de **buscar** con opciones de buscar siguiente y buscar anterior.
- Función de **reemplazar** texto.
- **Contador de palabras, caracteres y tiempo de lectura** en la barra de estado, implementado como componente reutilizable (`WordCounterWidget`).
- **Dictado por voz** con comandos de voz para negrita, cursiva, subrayado, guardar y nuevo documento.
- Interfaz organizada con menús y barras de herramientas para acceder rápido a las funciones principales.

## Captura de la aplicación

A continuación se muestra una captura de la interfaz principal de **MiniOffice**, donde se pueden ver los menús, la barra de herramientas y el área de edición:
<img width="1133" height="792" alt="image" src="https://github.com/user-attachments/assets/4dcc0dbd-335b-4f7a-acd5-3ce32077a48e" />

---

## Documentación de Señales (Signals)

### ¿Qué son las señales en PySide6/Qt?

Las **señales (Signals)** son un mecanismo fundamental del framework Qt que permite la comunicación entre objetos de forma desacoplada. Cuando ocurre un evento (por ejemplo, un clic de botón o un cambio de texto), el objeto emisor **emite** una señal. Otros objetos pueden **conectarse** a esa señal mediante un **slot** (función receptora) para reaccionar al evento.

**Ventajas de usar señales:**
- **Desacoplamiento**: el emisor no necesita conocer al receptor.
- **Reutilización**: los componentes se pueden usar en diferentes contextos conectando sus señales a distintos slots.
- **Mantenibilidad**: facilita separar la lógica de la interfaz.

---

### Señales definidas en el proyecto

| Señal | Clase | Tipo de datos emitidos | Descripción |
|---|---|---|---|
| `conteoActualizado` | `WordCounterWidget` | `int, int` (palabras, caracteres) | Se emite cada vez que se actualiza el conteo de palabras y caracteres del texto. |
| `recognized` | `VoiceWorker` | `str` (texto reconocido) | Se emite cuando el motor de voz transcribe correctamente el audio del micrófono. |
| `status` | `VoiceWorker` | `str` (mensaje de estado) | Se emite para informar del estado del proceso de reconocimiento de voz (calibrando, escuchando, transcribiendo, error). |

---

### Señales nativas de Qt utilizadas

| Señal | Objeto | Descripción |
|---|---|---|
| `textChanged` | `QTextEdit` (editor) | Se emite cada vez que el contenido del editor cambia. Conectada al temporizador que dispara la actualización del contador. |
| `timeout` | `QTimer` (timer_palabras) | Se emite cuando el temporizador de 200 ms expira. Conectada a `actualizar_contador_palabras()`. |
| `triggered` | `QAction` | Se emite cuando el usuario activa una acción (menú o barra de herramientas). |
| `clicked` | `QPushButton` | Se emite cuando se pulsa un botón (buscar abajo, arriba, todas). |

---

### Componente reutilizable: `WordCounterWidget`

El archivo `word_counter_widget.py` contiene un widget reutilizable que muestra el conteo de palabras, caracteres y el tiempo de lectura estimado.

#### Propiedades del constructor

| Parámetro | Tipo | Valor por defecto | Descripción |
|---|---|---|---|
| `wpm` | `int` | `200` | Palabras por minuto para calcular el tiempo de lectura. |
| `mostrarPalabras` | `bool` | `True` | Muestra/oculta la etiqueta de palabras. |
| `mostrarCaracteres` | `bool` | `True` | Muestra/oculta la etiqueta de caracteres. |
| `mostrarTiempoLectura` | `bool` | `True` | Muestra/oculta la etiqueta de tiempo de lectura. |
| `parent` | `QWidget` | `None` | Widget padre. |

#### Métodos

| Método | Descripción |
|---|---|
| `update_from_text(text: str)` | Recibe el texto del editor, calcula palabras (con regex `\b\w+\b`), caracteres y tiempo de lectura, actualiza las etiquetas y emite la señal `conteoActualizado`. |
| `_apply_visibility()` | Aplica la visibilidad de cada etiqueta según los parámetros del constructor. |

#### Señal emitida

```python
conteoActualizado = Signal(int, int)  # (palabras, caracteres)
```

Se emite cada vez que se llama a `update_from_text()`. Permite a la ventana principal u otros componentes reaccionar al cambio de conteo.

#### Ejemplo de uso

```python
from word_counter_widget import WordCounterWidget

# Crear el widget
contador = WordCounterWidget(wpm=200, mostrarPalabras=True, mostrarCaracteres=True, mostrarTiempoLectura=True)

# Conectar la señal a un slot
contador.conteoActualizado.connect(lambda p, c: print(f"Palabras: {p}, Caracteres: {c}"))

# Actualizar desde texto
contador.update_from_text("Hola mundo, esto es una prueba")
# Salida: Palabras: 6, Caracteres: 30
```

---

### Diagrama de conexiones de señales

```
┌──────────────┐    textChanged     ┌──────────────────┐
│   QTextEdit  │ ─────────────────> │  QTimer (200ms)  │
│   (editor)   │                    │ timer_palabras    │
└──────────────┘                    └────────┬─────────┘
                                             │ timeout
                                             ▼
                                  ┌─────────────────────┐
                                  │ actualizar_contador  │
                                  │    _palabras()       │
                                  └────────┬────────────┘
                                           │ update_from_text(texto)
                                           ▼
                                  ┌─────────────────────┐
                                  │ WordCounterWidget    │
                                  │ - lblP (Palabras)    │
                                  │ - lblC (Caracteres)  │
                                  │ - lblT (Lectura)     │
                                  └────────┬────────────┘
                                           │ conteoActualizado(int, int)
                                           ▼
                                  ┌─────────────────────┐
                                  │ on_conteo_actualizado│
                                  │ → barra de estado   │
                                  └─────────────────────┘
```

---

## Ejecución con Python

1. Instalar Python.
2. Instalar las librerías necesarias:
   ```bash
   pip install PySide6 SpeechRecognition PyAudio
   ```
3. Ejecutar el programa desde la terminal (ubicado en la carpeta del proyecto):
   ```bash
   python MiniOffice.py
   ```
