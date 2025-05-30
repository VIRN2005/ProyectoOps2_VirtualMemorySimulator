# 📦 Simulador de Memoria Virtual

Este script en Python simula la **gestión de memoria virtual** utilizando distintos algoritmos de **reemplazo de página**: `FIFO`, `LRU` y `OPT`. Procesa un archivo de trazas de acceso a memoria y calcula métricas clave como **fallos de página**, **reemplazos**, **escrituras a disco** y el **Tiempo de Acceso Efectivo (EAT)**.

---

## 🧠 Características

- Simula las políticas de reemplazo: **FIFO**, **LRU** y **Óptimo (OPT)**.
- Soporta operaciones de lectura y escritura en memoria.
- Calcula:
  - Total de **fallos de página**
  - Número de **reemplazos**
  - Número de **escrituras a disco** (cuando se elimina una página sucia)
  - **Tiempo de Acceso Efectivo (EAT)**
- Procesamiento eficiente de archivos de traza grandes con `tqdm` (barra de progreso).
- Paso de preprocesamiento para OPT que analiza accesos futuros.

---

## 🚀 Uso

### 🔧 Requisitos

- Python 3.x
- tqdm (`pip install tqdm`)

### ▶️ Ejecutar el Simulador

```bash
python Virtual_Memory_Simulator.py <ruta_al_archivo_de_traza>
````

### Ejemplo:

```bash
python Virtual_Memory_Simulator.py gcc.trace
```

---

## ⚙️ Configuración

Los siguientes valores están definidos dentro del código y pueden modificarse:

```python
frame_counts = [10, 50, 100]           # Cantidad de marcos de página
replacement_policies = ['FIFO', 'LRU', 'OPT']  # Algoritmos a simular
```

---

## 📊 Salida

El programa muestra un resumen por cada configuración:

```
Frames | Política | Page Faults | Reemplazos | Escrituras | EAT (ns)  | Tiempo (s)
-------------------------------------------------------------------------------
    10 | FIFO     |       12,345 |     12,345 |      3,456 | 234567.89 |     3.21
    10 | LRU      |       10,987 |     10,987 |      2,345 | 198765.43 |     2.97
    ...
```

---

## 📁 Formato del Archivo de Traza

Cada línea del archivo `.trace` debe tener:

```
<dirección_hexadecimal> <operación>
```

Ejemplo:

```
0x0040A23F R
0x0010B23A W
```

* `R` = Lectura
* `W` = Escritura

---

## 🧠 ¿Cómo funciona?

* **FIFO**: Reemplaza la página cargada más antigua.
* **LRU**: Reemplaza la página menos recientemente usada.
* **OPT**: Reemplaza la página que no se usará en el mayor tiempo futuro (requiere conocer las futuras referencias).

---

## 📌 Notas

* El **EAT (Tiempo de Acceso Efectivo)** se calcula considerando:

  * Tiempo de acceso a memoria: 100 ns
  * Tiempo de fallo de página: 10 ms (10,000,000 ns)

---
