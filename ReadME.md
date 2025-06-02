# 🚀 Simulador Avanzado de Gestión de Memoria Virtual

Este simulador en Python implementa un **sistema completo de gestión de memoria virtual** con múltiples algoritmos de **reemplazo de página** y análisis estadístico avanzado. Procesa archivos de trazas de acceso a memoria y proporciona métricas detalladas de rendimiento.

---

## 🧠 Características Principales

### Algoritmos de Reemplazo Implementados
- **FIFO** (First In, First Out) - Reemplaza la página más antigua
- **LRU** (Least Recently Used) - Reemplaza la página menos recientemente usada
- **LFU** (Least Frequently Used) - Reemplaza la página menos frecuentemente usada
- **CLOCK** - Algoritmo de segunda oportunidad con bit de referencia
- **OPT** (Óptimo) - Reemplaza la página que no se usará por más tiempo (requiere preprocesamiento)

### Métricas Calculadas
- **Fallos de página** (Page Faults)
- **Tasa de aciertos** (Hit Rate)
- **Número de reemplazos**
- **Escrituras a disco** (cuando se elimina una página sucia)
- **Tiempo de Acceso Efectivo (EAT)**
- **Estadísticas de operaciones** (lecturas vs escrituras)
- **Páginas únicas accedidas**
- **Frecuencia de acceso por página**

### Características Avanzadas
- 🎨 **Interfaz colorida** con tablas formateadas y barras de progreso
- ⚡ **Procesamiento eficiente** de archivos grandes con `tqdm`
- 📊 **Análisis estadístico completo** con comparaciones de rendimiento
- 💾 **Exportación de resultados** en formato JSON
- 🔧 **Parser de argumentos** flexible para configuración personalizada
- 📈 **Visualización en tiempo real** opcional

---

## 🚀 Instalación y Uso

### 🔧 Requisitos

```bash
pip install tqdm
```

Requiere **Python 3.x**

### ▶️ Uso Básico

```bash
python Virtual_Memory_Simulator.py <archivo_de_traza>
```

### ▶️ Uso Avanzado

```bash
# Configuración personalizada de frames y políticas
python Virtual_Memory_Simulator.py trace.txt --frames 10 50 100 --policies FIFO LRU OPT

# Guardar resultados en JSON
python Virtual_Memory_Simulator.py trace.txt --save-json resultados.json

# Mostrar estadísticas en tiempo real
python Virtual_Memory_Simulator.py trace.txt --realtime

# Probar todos los algoritmos
python Virtual_Memory_Simulator.py trace.txt --policies FIFO LRU LFU CLOCK OPT
```

### 📋 Opciones de Línea de Comandos

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `trace_file` | Archivo de traza (requerido) | `trace.txt` |
| `--frames` | Número de frames a probar | `--frames 10 25 50 100` |
| `--policies` | Algoritmos a simular | `--policies FIFO LRU OPT` |
| `--save-json` | Guardar resultados en JSON | `--save-json results.json` |
| `--realtime` | Mostrar estadísticas en tiempo real | `--realtime` |

---

## ⚙️ Configuración Predeterminada

```python
# Configuración por defecto en el código
frame_counts = [10, 50, 100]           # Cantidad de marcos de página
replacement_policies = ['FIFO', 'LRU', 'OPT']  # Algoritmos a simular

# Tiempos para cálculo de EAT
MEMORY_ACCESS_TIME = 100          # nanosegundos
PAGE_FAULT_TIME = 10_000_000     # nanosegundos (10ms)
```

---

## 📊 Formato de Salida

### Tabla de Resultados Principales
```
┌────────┬──────────┬─────────────┬───────────┬─────────────┬────────────┐
│ Frames │ Política │ Page Faults │  Hit Rate │   EAT (ns)  │ Tiempo (s) │
├────────┼──────────┼─────────────┼───────────┼─────────────┼────────────┤
│     10 │   FIFO   │    12,345   │   87.65%  │  234,567.89 │    3.21    │
│     10 │    LRU   │    10,987   │   89.23%  │  198,765.43 │    2.97    │
│     10 │    OPT   │     9,876   │   90.12%  │  187,654.32 │    4.15    │
└────────┴──────────┴─────────────┴───────────┴─────────────┴────────────┘
```

### Estadísticas Detalladas por Simulación
- **Page Faults**: Número total de fallos de página
- **Hit Rate**: Porcentaje de accesos que resultaron en acierto
- **Fault Rate**: Porcentaje de accesos que resultaron en fallo
- **Replacements**: Número de reemplazos de página realizados
- **Disk Writes**: Escrituras a disco por páginas sucias
- **EAT**: Tiempo de Acceso Efectivo en nanosegundos
- **Reads/Writes**: Distribución de operaciones de lectura y escritura
- **Unique Pages**: Número de páginas únicas accedidas

### Mejores Rendimientos
El simulador identifica automáticamente:
- 🥇 **Mejor Hit Rate**: Algoritmo con mayor tasa de aciertos
- 🥇 **Mejor EAT**: Algoritmo con menor tiempo de acceso efectivo
- 🥇 **Más Rápido**: Algoritmo con menor tiempo de ejecución

---

## 📁 Formato del Archivo de Traza

Cada línea debe contener una dirección hexadecimal seguida de la operación:

```
<dirección_hexadecimal> <operación>
```

### Ejemplo:
```
0x0040A23F R
0x0010B23A W
0x00508000 R
0x0040A240 W
```

**Operaciones soportadas:**
- `R` = Lectura (Read)
- `W` = Escritura (Write)

---

## 🔬 Funcionamiento de los Algoritmos

### FIFO (First In, First Out)
- Mantiene una cola de páginas en orden de llegada
- Reemplaza siempre la página más antigua
- Implementación: `deque` para eficiencia O(1)

### LRU (Least Recently Used)
- Rastrea el orden de uso de las páginas
- Reemplaza la página menos recientemente usada
- Implementación: `OrderedDict` para acceso O(1)

### LFU (Least Frequently Used)
- Cuenta la frecuencia de acceso de cada página
- En caso de empate, usa el tiempo de último acceso
- Implementación: Contadores con timestamps

### CLOCK (Segunda Oportunidad)
- Utiliza un bit de referencia circular
- Da una "segunda oportunidad" a páginas referenciadas
- Implementación: Puntero circular con bits de referencia

### OPT (Óptimo de Belady)
- Requiere conocimiento futuro de referencias
- Reemplaza la página que se usará más tarde en el futuro
- Implementación: Preprocesamiento completo del archivo

---

## 📈 Exportación de Resultados

### Formato JSON
```json
{
  "timestamp": "2024-12-01T10:30:00",
  "results": [
    {
      "frames": 10,
      "policy": "FIFO",
      "page_faults": 12345,
      "hit_rate": 87.65,
      "eat": 234567.89,
      "execution_time": 3.21,
      "total_accesses": 100000,
      "unique_pages": 2500
    }
  ],
  "summary": {
    "total_simulations": 9,
    "policies_tested": ["FIFO", "LRU", "OPT"],
    "frame_counts_tested": [10, 50, 100]
  }
}
```

---

## 🎯 Casos de Uso

### Investigación Académica
- Comparación de algoritmos de reemplazo de página
- Análisis de patrones de acceso a memoria
- Estudios de localidad temporal y espacial

### Optimización de Sistemas
- Evaluación de configuraciones de memoria
- Análisis de rendimiento de aplicaciones
- Tuning de sistemas operativos

### Educación
- Demostración visual de algoritmos de SO
- Análisis comparativo de políticas
- Comprensión de conceptos de memoria virtual

---

## 📌 Notas Técnicas

### Cálculo del EAT
```
EAT = Tiempo_Acceso_Memoria + (Tasa_Fallos × Tiempo_Fallo_Página)
EAT = 100ns + (fault_rate × 10,000,000ns)
```

### Optimizaciones Implementadas
- **Preprocesamiento inteligente** para el algoritmo OPT
- **Estructuras de datos eficientes** (deque, OrderedDict)
- **Conteo rápido de líneas** para archivos grandes
- **Barras de progreso** para archivos que requieren mucho procesamiento

### Limitaciones
- El algoritmo OPT requiere dos pasadas por el archivo
- El consumo de memoria es proporcional al número de páginas únicas
- Los archivos extremadamente grandes pueden requerir mucho tiempo de preprocesamiento

---

## 👨‍💻 Autor

**Víctor Romero** - 12211079

---

## 🏆 Características Destacadas

- ✅ **5 algoritmos de reemplazo** implementados
- ✅ **Interfaz visual atractiva** con colores y tablas
- ✅ **Análisis estadístico completo**
- ✅ **Exportación flexible** de resultados
- ✅ **Configuración personalizable**
- ✅ **Manejo eficiente** de archivos grandes
- ✅ **Comparación automática** de rendimiento