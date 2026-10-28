---
name: analizar-figuras-articulos
description: Leer el texto incrustado de un PDF científico y, además, interpretar sus figuras, gráficas, diagramas y tablas usando capacidades de visión del LLM. Útil cuando el resumen textual no basta y hay que entender qué muestra una curva de aprendizaje, un diagrama de arquitectura o una tabla de resultados. Triggers: entender la figura, interpretar gráfica, leer gráfica paper, qué muestra la figura, análisis visual paper, curva de aprendizaje, diagrama arquitectura, tabla de resultados.
---

# Analizar figuras y gráficas de artículos científicos

El PDF es texto **más** imágenes. La tool `Read` lee el texto incrustado de un PDF directamente; para las figuras hay que rasterizar la página y pasársela al LLM como imagen (multimodal). Esta skill coordina ambas cosas en un subagente.

## Herramientas necesarias

El agente usará **PowerShell/Bash + Python** con los siguientes paquetes (pre-instalados en Python típico, instala con pip si faltan):

- `pymupdf` (import `fitz`) → rasteriza páginas y extrae imágenes individuales.
- `pdfplumber` → tablas estructuradas.
- `Pillow` → recortes.

Si no están, instalar en el entorno virtual del usuario (preguntar antes si procede).

## Flujo

1. **Extraer texto plano** del PDF con `Read` (o `fitz.open(path).get_text()`).
2. **Localizar figuras**: regex sobre el texto para encontrar `Fig. 1`, `Figure 2`, `Table 3`, y su caption.
3. **Rasterizar**: por cada página con figura, convertir a PNG a 200 dpi en el scratchpad.
4. **Recortar** (opcional) la bounding-box de la figura con `fitz` para evitar que el LLM se distraiga con el resto de la página.
5. **Pasar la imagen al LLM**: dentro del subagente, llamar a `Read` con el PNG — las imágenes se renderizan nativamente al modelo.
6. **Describir y relacionar** la figura con el caption y el texto que la referencia.

## Prompt para el subagente

Lanza un `general-purpose` agent con:

```
Analiza las figuras y tablas del siguiente PDF científico y describe lo que
muestran para su uso en el TFM del usuario (RL para navegación map-less de AGVs).

Fichero: <RUTA_PDF>
Páginas / figuras de interés: <LISTA | "todas las que tengan Fig./Table">

Pasos:

1. Lee el texto completo del PDF con `Read` (usa `pages:"1-20"` si >10 páginas y
   repite por tramos).
2. Extrae los captions de todas las figuras y tablas (patrón regex sobre texto).
3. Rasteriza las páginas correspondientes a 200 dpi con un script Python como:

   ```python
   import fitz, sys, pathlib
   src, outdir = sys.argv[1], pathlib.Path(sys.argv[2]); outdir.mkdir(exist_ok=True)
   doc = fitz.open(src)
   for i, p in enumerate(doc):
       pix = p.get_pixmap(dpi=200)
       pix.save(outdir / f"page_{i+1:03d}.png")
   ```

   Guarda las PNG en `<scratchpad>/figs/`.
4. Para cada figura/tabla relevante, abre la imagen con `Read` (eso la expone
   al LLM) y escribe una explicación con esta plantilla:

   ### Figura N — <caption resumido>
   - **Qué representa:** 1-2 frases
   - **Ejes / variables:** eje X = …, eje Y = …, series = …
   - **Lectura cuantitativa:** valores aproximados en puntos clave
     (ej.: "a los 2M pasos, PPO alcanza success rate ≈ 0.85 vs. DQN ≈ 0.62")
   - **Interpretación:** qué conclusión soporta esta figura dentro del paper
   - **Relación con el texto:** cita el párrafo que la referencia
   - **Alertas:** ¿eje log?, ¿nº semillas?, ¿barra de error?, ¿cherry-picking?

5. Para tablas, prefiere **extraer con `pdfplumber`** y reproducir el contenido
   en Markdown antes de interpretarla, para no "alucinar" valores:

   ```python
   import pdfplumber
   with pdfplumber.open(src) as pdf:
       for t in pdf.pages[P-1].extract_tables():
           print(t)
   ```

6. Al final, entrega un fichero `analisis_figuras_<cite_key>.md` con todas las
   descripciones y guarda las PNG recortadas junto a él.

Importante: NO inventes números. Si una curva es ilegible dilo. Si una
figura es un diagrama de bloques, descríbelo como arquitectura (bloques,
flechas, entradas/salidas), no como gráfica.
```

## Qué devolver en chat

- Lista de figuras/tablas analizadas (una línea por cada una).
- 3-5 bullets con lo más jugoso para el TFM.
- Ruta absoluta del informe + del directorio de PNGs.

## Casos especiales

- **Papers escaneados** (sin texto incrustado): avisar al usuario, aplicar OCR con `pytesseract` solo si lo permite.
- **Figuras compuestas** (subfiguras a/b/c/d): recorta y numera cada subfigura por separado.
- **Diagramas vectoriales**: a veces conviene extraer el SVG embebido en vez de rasterizar.
