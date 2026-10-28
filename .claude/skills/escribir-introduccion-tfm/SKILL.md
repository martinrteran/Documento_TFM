---
name: escribir-introduccion-tfm
description: Redactar la Introducción de un Trabajo de Fin de Máster en LaTeX, en español académico, imitando el estilo de uno o varios ficheros de ejemplo que el usuario indique (voz, longitud de frase, cadencia de citas, uso de \citep, estructura de secciones Motivación / Propuesta y objetivos / Estructura del documento). Triggers: escribe la introducción, redacta introducción, intro TFM, chapter introduccion, inicio tesis, apartado 1, motivación tesis.
---

# Escribir la Introducción del TFM imitando un estilo

Esta skill lanza un **subagente** `general-purpose` (o `anthropic-skills:academic-thesis-writer` si está disponible) que:

1. Lee los **ficheros de estilo** que el usuario proporcione (por defecto `capitulos/1.introduccion.tex` y `capitulos/introduccion.tex`).
2. Lee los materiales fuente que haya que resumir (resúmenes previos, `bibliografia.bib`, notas del usuario).
3. Produce la nueva Introducción en `.tex` listo para `\input`.

## Entrada

El usuario debe (o puede) proveer:

- `--estilo <ficheros>`: lista de `.tex` de ejemplo (los suyos previos o de un autor que admire).  Default: `capitulos/1.introduccion.tex`.
- `--tema`: el enfoque concreto del nuevo capítulo si difiere.
- `--objetivos`: lista de objetivos específicos a incluir.
- `--longitud`: nº aproximado de palabras (default 1500-2500).
- `--secciones`: por defecto `Motivación`, `Propuesta y objetivos`, `Estructura del documento`.
- `--referencias`: claves BibTeX que deben aparecer (ya existentes en `bibliografia.bib`).

Si falta algo, el agente pregunta al usuario antes de empezar — nunca invente objetivos del TFM.

## Prompt para el subagente

```
Rol: eres un redactor de tesis técnicas de ingeniería en español académico formal.

Objetivo: escribir el capítulo "Introducción" de un TFM sobre
<TEMA>  (default del repo: navegación map-less de AGVs con DRL).

Pasos obligatorios ANTES de escribir:

1. Lee cada fichero en --estilo y haz una ficha interna del estilo:
   - Longitud media de frase y de párrafo.
   - Densidad de citas por párrafo (ej. "1-2 \citep{} por párrafo").
   - Vocabulario: ¿usa anglicismos entre comillas simples, cursivas con
     \textit{}, acrónimos entre paréntesis la primera vez?
   - Estructura de secciones y subsecciones.
   - Uso de listas, tablas y acrónimos.
   - Tono: 1ª persona plural ("hemos", "proponemos") vs. impersonal.
2. Lee `bibliografia.bib` para saber qué \citep{clave} son válidas. **NUNCA
   cites una clave que no esté ahí.** Si falta una referencia necesaria,
   deja un `\citep{PENDIENTE_breve_descripcion}` y lístalo al final del
   output para que el usuario la añada.
3. Lee `Documento_maestro.tex` para respetar paquetes LaTeX disponibles
   (natbib, glossaries, hyperref, etc.) y los comandos ya definidos.

Reglas de salida:

- Entregable: UN fichero `.tex` autocontenido que empieza por
  `\chapter{Introducción}\label{chap:introduccion}` y usa `\section` /
  `\subsection` como el estilo de referencia.
- Español peninsular académico, impersonal o 1ª p. plural (coherente con los
  ejemplos). Nada de "yo".
- Siglas y acrónimos: la primera vez `Vehículo de Guiado Automático (AGV)`
  y a partir de ahí "AGV". Añadir al glosario si el proyecto usa
  `glossaries`.
- Citas con `\citep{clave}` siguiendo la densidad del estilo.
- No inventar números concretos (p. ej. "los AGV reducen un 37 % el
  tiempo") sin referencia real.
- Terminar con una sección "Estructura del documento" que describa en
  párrafos (no bullets) los capítulos siguientes del TFM.

Longitud: ~<N> palabras (default 1800).

Entrega el .tex en el fichero `<ruta_destino>` y, en el mensaje final, un
resumen con:
- Nº de palabras real.
- Lista de `\citep{...}` usadas.
- Lista de referencias PENDIENTES por añadir a `bibliografia.bib`.
- Diferencias detectadas respecto al estilo de referencia (si hubo
  concesiones).
```

## Dónde escribir

- Default: `capitulos/1.introduccion.tex` **en una copia nueva** `capitulos/1.introduccion.nueva.tex`. **No sobrescribir** el fichero original hasta que el usuario confirme.
- Al confirmar, mueve con `git mv` para preservar historial.

## Compilación de validación

Antes de dar por buena la escritura, el agente debe comprobar que el fichero compila. Desde el directorio raíz del TFM:

```bash
pdflatex -interaction=nonstopmode -halt-on-error Documento_maestro.tex \
  && bibtex Documento_maestro \
  && pdflatex -interaction=nonstopmode Documento_maestro.tex \
  && pdflatex -interaction=nonstopmode Documento_maestro.tex
```

Si no se puede ejecutar LaTeX, hacer al menos una revisión sintáctica con `chktex capitulos/1.introduccion.nueva.tex`.

## Qué devolver en chat

- Ruta al `.tex` generado.
- Nº de palabras.
- Lista de citas usadas y pendientes.
- Pregunta explícita: "¿Lo pongo como fichero oficial reemplazando a `1.introduccion.tex`?" — nunca sobrescribir sin confirmación.
