---
name: resumir-articulos-cientificos
description: Resumir artículos científicos (PDF local, URL o DOI) extrayendo los puntos más importantes para una tesis o estado del arte. Produce un resumen estructurado en español con problema, enfoque, método, datos/experimentos, resultados cuantitativos, limitaciones, aportaciones y utilidad para el TFM. Triggers: resumir paper, resumen artículo, resumir PDF, extraer puntos clave, abstract extendido, qué dice este paper, destripar artículo, review paper.
---

# Resumir artículos científicos

Esta skill lanza un **subagente** `general-purpose` que lee el artículo (local o remoto) y entrega un resumen estructurado. Se delega para no cargar el PDF entero en el contexto principal.

## Entrada admitida

- Ruta local a un PDF (ej. `otros/paper.pdf`).
- URL http(s) a un PDF o a la página del artículo.
- DOI o arXiv ID (el agente resuelve el PDF).
- Varias referencias a la vez: produce un resumen por cada una, más una tabla comparativa.

## Prompt para el agente

```
Resume el siguiente artículo científico para su uso en un Trabajo de Fin de Máster sobre
navegación map-less de AGVs mediante Aprendizaje por Refuerzo Profundo (DRL):

Fuente: <RUTA_O_URL_O_DOI>

Si es un PDF local, léelo con la tool `Read` (soporta PDFs; para >10 páginas usa el
parámetro `pages` por tramos de 20). Si es URL/DOI, descárgalo primero con WebFetch
(o resuelve el DOI vía `https://doi.org/<DOI>` y busca el PDF). Guarda el PDF
descargado en el scratchpad; no lo subas al repositorio del TFM salvo que el
usuario lo pida.

Entrega un resumen EN ESPAÑOL con esta plantilla exacta (Markdown):

# <Título corto> — <Primer autor et al., AÑO>

**Cita BibTeX:** una entrada BibTeX válida (si falta, construye una coherente con
Autor-Año-TítuloCorto como clave).

## 1. Problema y motivación
2-4 frases: qué problema concreto aborda y por qué importa.

## 2. Enfoque / Hipótesis
Qué proponen los autores en una frase + el supuesto clave.

## 3. Método
- Formulación matemática (MDP, POMDP, función de valor, etc. si aplica).
- Arquitectura (red neuronal, algoritmo RL concreto: DQN, PPO, SAC...).
- Pseudocódigo o diagrama de bloques resumido en 5-10 líneas.
- Hiperparámetros destacados.

## 4. Datos y experimentos
- Entornos / dataset / simulador (Gazebo, Gym, Isaac, real-world, ...).
- Métricas usadas (success rate, SPL, tiempo, colisiones, retorno, etc.).
- Baselines con los que comparan.

## 5. Resultados cuantitativos
Tabla breve o viñetas con los números concretos frente a los baselines.

## 6. Limitaciones y supuestos
Lo que los autores reconocen que no funciona, y lo que te parece débil tras leerlo
críticamente (sé honesto; no inventes).

## 7. Aportaciones (novedad)
Qué es realmente nuevo, en una lista de 2-4 ítems.

## 8. Utilidad para este TFM
¿Qué de este paper puede citarse, replicarse o contrastarse en el TFM del usuario?
Sugiere en qué sección encaja: Introducción, Estado del Arte, Metodología,
Discusión. Da la cita \citep{clave} que podría usarse.

## 9. Preguntas abiertas / Trabajo futuro
Lo que el paper deja sin resolver.

Longitud objetivo: 500-900 palabras por paper. No reproduzcas párrafos literales
del artículo (parafrasea). Si una sección no aplica, pon "No reportado" en vez de
inventar.
```

## Si el usuario pasa varios artículos

Añade al final del informe una tabla comparativa:

```
| Paper | Método | Entorno | Métrica clave | Resultado | Año |
|-------|--------|---------|---------------|-----------|-----|
```

y una sección "Síntesis cruzada" (3-5 bullets) con los puntos comunes y las divergencias.

## Dónde guardar los resúmenes

- Por defecto en el scratchpad del usuario como `resumen_<cite_key>.md`.
- Si el usuario dice "añádelo al TFM", crea el fichero en `otros/resumenes/` dentro del repo (crea el directorio si no existe) y haz commit **solo si el usuario lo pide**.

## Qué devolver en chat

Al terminar, muestra:
1. Cita en una línea.
2. Las 3-5 ideas clave en viñetas.
3. La ruta absoluta del fichero completo.
