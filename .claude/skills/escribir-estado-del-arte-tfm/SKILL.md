---
name: escribir-estado-del-arte-tfm
description: Redactar el capítulo "Estado del Arte" de un TFM en LaTeX, en español académico, imitando el estilo de uno o varios ficheros de ejemplo, con revisión crítica de la literatura, agrupación temática, comparativas y detección de huecos de investigación. Triggers: estado del arte, state of the art, SOTA, literatura, revisión bibliográfica tesis, capítulo 2, chapter 2, antecedentes.
---

# Escribir el Estado del Arte del TFM

Esta skill lanza un **subagente** `general-purpose` (o el skill `anthropic-skills:academic-thesis-writer` cuando esté disponible) que redacta un Estado del Arte crítico, no un listado de resúmenes.

## Diferencia con "Trabajos Relacionados"

- **Estado del Arte**: panorámica amplia del campo (fundamentos + principales líneas + evolución histórica + técnicas vigentes + huecos). Más largo.
- **Trabajos Relacionados / Anteriores Referentes**: focalizado en papers que atacan **el mismo problema** que el TFM. Más corto y comparativo. Ver `escribir-trabajos-relacionados-tfm`.

## Entrada

- `--estilo <ficheros>`: `.tex` de ejemplo. Default `capitulos/2.estado_del_arte.tex` y `capitulos/estado_del_arte.tex`.
- `--referencias`: BibTeX keys obligatorias o un fichero de resúmenes previos (ver skill `resumir-articulos-cientificos`).
- `--ejes`: dimensiones de clasificación (ej.: "clásicos vs aprendizaje", "map-based vs map-less", "value-based vs policy-based"). Si no se dan, el agente propone 2-4.
- `--longitud`: default 3000-5000 palabras.

## Prompt para el subagente

```
Rol: investigador académico en Robótica + RL, estilo tesis española en LaTeX.

Objetivo: redactar el capítulo "Estado del Arte" para un TFM sobre
<TEMA_TFM>. No es un volcado de resúmenes: es una narrativa crítica
estructurada por ejes.

Fase 1 — Preparación:
1. Lee los ficheros --estilo y extrae: longitud de frase, densidad de citas,
   organización por secciones, uso de tablas comparativas, cadencia de
   transiciones ("A continuación…", "Por otro lado…", "Pese a lo
   anterior…").
2. Lee `bibliografia.bib`. Si --referencias apunta a resúmenes previos,
   léelos para no reinventar hallazgos. **No cites claves inexistentes**.
3. Pide al usuario los ejes de clasificación si no vinieron por parámetro.

Fase 2 — Estructura obligatoria del capítulo:

\chapter{Estado del Arte}
\section{Fundamentos y evolución histórica}
  Breve recorrido cronológico del subcampo.
\section{<Eje 1>}
\section{<Eje 2>}
\section{<Eje N>}
\section{Comparativa}
  TABLA LaTeX comparando los ~8-15 trabajos más citados por eje:
    columnas típicas = Trabajo (\citep), Año, Enfoque, Entorno,
    Métricas, Fortalezas, Debilidades.
\section{Huecos de investigación}
  2-4 lagunas detectadas que motivan el TFM. Esta sección es
  OBLIGATORIA porque enlaza con la motivación del capítulo 1.

Fase 3 — Reglas de redacción:

- Cada afirmación con número o resultado concreto DEBE llevar \citep.
- Prohibido "muchos autores" / "varios estudios" sin cita.
- Agrupa trabajos en lugar de narrarlos uno por uno:
  "Los enfoques basados en Q-learning profundo \citep{a, b, c} comparten
  la limitación de X, abordada mediante Y en \citep{d}." — mejor que un
  párrafo por paper.
- Cursiva \textit{} para términos ingleses sin traducción estándar.
- Siglas la primera vez con su definición y a partir de ahí la sigla sola.
- Nada de autoreferencia al propio TFM ("en esta tesis demostramos…"); eso
  va en la Introducción y las Conclusiones.

Fase 4 — Validación:
- Comprueba que todas las \citep{clave} existen en bibliografia.bib
  (haz grep). Lista las PENDIENTES.
- Verifica que no hay ninguna cita duplicada en la tabla y en el texto
  en el mismo párrafo (evita el "ping-pong" de citas).
- Longitud entre --longitud ± 15 %.

Entrega: fichero `.tex` autocontenido en <ruta_destino>, por defecto
`capitulos/2.estado_del_arte.nueva.tex`.
```

## Dónde escribir

Mismo criterio que la Introducción:

- Default: `capitulos/2.estado_del_arte.nueva.tex`.
- Reemplazar al original solo tras confirmación del usuario.

## Validación LaTeX

El agente intenta compilar y, si hay errores, los reporta sin tocar el fichero original. Comando:

```bash
pdflatex -interaction=nonstopmode -halt-on-error Documento_maestro.tex
```

## Qué devolver en chat

- Ruta del `.tex` nuevo.
- Nº de citas usadas / nº de citas pendientes.
- Tabla comparativa (número de filas y columnas) para que el usuario la vea de un vistazo.
- Lista de "huecos de investigación" detectados — útiles también para la Introducción.
