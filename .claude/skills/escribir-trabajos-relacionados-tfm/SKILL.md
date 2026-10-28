---
name: escribir-trabajos-relacionados-tfm
description: Redactar la sección o capítulo "Trabajos Anteriores Referentes" / "Trabajos Relacionados" / "Related Works" del TFM en LaTeX, español académico. Focalizado en los papers que atacan el MISMO problema del TFM, con tabla comparativa punto a punto y argumentación clara de qué aporta este TFM frente a cada uno. Puede imitar un estilo dado. Triggers: trabajos relacionados, related work, trabajos anteriores, antecedentes directos, trabajos referentes, comparación con la literatura, qué aporta mi tesis.
---

# Escribir "Trabajos Anteriores Referentes" del TFM

Es un primo focalizado del Estado del Arte. Aquí **no** se hace panorámica: se compara el TFM contra los 5-15 trabajos más cercanos a su contribución.

## Diferencia clave

- **Estado del Arte**: todo el campo. Narrativa amplia.  → `escribir-estado-del-arte-tfm`
- **Trabajos Relacionados**: solo trabajos que resuelven el mismo problema (o un problema muy cercano) que el TFM. Siempre acaba con "qué distingue a este TFM".

## Entrada

- `--estilo <ficheros>`: `.tex` ejemplo.
- `--trabajos`: lista explícita de BibTeX keys que son "los competidores". Si no vienen, el agente llama a `buscar-articulos-scholar` o pregunta.
- `--contribucion`: resumen en 1-3 frases de la aportación propia del TFM (si no se da, se pregunta).
- `--longitud`: default 1200-2500 palabras.

## Prompt para el subagente

```
Rol: redactor académico español, muy preciso y comparativo.

Tarea: redactar la sección "Trabajos Anteriores Referentes" del TFM sobre
<TEMA_TFM>. Debe terminar con una explicación clara de qué aporta este
TFM frente a cada trabajo mencionado.

Preparación:
1. Lee los --estilo para heredar voz, tono, cadencia de citas y uso de
   tablas.
2. Lee `bibliografia.bib`. Si no están todos los --trabajos, invoca la
   skill `buscar-articulos-scholar` o deja `\citep{PENDIENTE_...}` y
   lista las referencias faltantes al final.
3. Lee los resúmenes previos si existen (`otros/resumenes/*.md`), para
   no reinventar lo que ya se analizó.

Estructura obligatoria:

\section{Trabajos Anteriores Referentes}

Párrafo 0 — bisagra: enuncia el problema concreto y por qué los
trabajos siguientes son especialmente relevantes.

Luego, agrupa en 2-3 subgrupos (por técnica o enfoque) y por cada
grupo:
  - Un párrafo introductorio del subgrupo.
  - Un párrafo por trabajo (o un párrafo por 2-3 trabajos muy
    parecidos), con el patrón:
      "En \citep{clave}, los autores proponen X para abordar Y, logrando
      Z en el entorno W. No obstante, su enfoque [limitación concreta
      que motiva el nuestro]."

Tabla comparativa (siempre al final, antes de la bisagra):

\begin{table}[htbp]
\begin{tabular}{llcccccl}
  Trabajo & Año & Técnica & Entorno & Métrica1 & Métrica2 & Open-source & Aportación propia frente a él \\
  \citep{a} & 2023 & PPO & Gazebo & SR 0.78 & 1.2 m/s & ✓ & nuestro añade X \\
  ...
\end{tabular}
\end{table}

Cierre OBLIGATORIO:

\subsection{Posicionamiento de este TFM}
Un párrafo con "A diferencia de los trabajos anteriores, en este TFM
se propone <contribucion> que (a) soluciona la limitación L1 observada
en \citep{a,b}, (b) incorpora C2 ausente en \citep{c}, y (c) se evalúa
en el escenario E que ninguno de los trabajos citados cubre."

Reglas duras:

- Toda limitación atribuida a un trabajo DEBE poder justificarse leyendo
  ese paper. Si no has leído el paper, usa la skill
  `resumir-articulos-cientificos` o pide los resúmenes antes de escribir.
  No inventar limitaciones.
- No afirmar que algo es "el primero en" sin evidencia. Preferir "uno de
  los primeros" o "entre los pioneros".
- No comparar métricas de entornos distintos como si fueran
  comparables.  Marcarlo en nota al pie si procede.
- En la columna "Aportación propia frente a él" la frase debe ser
  concreta y verificable; nada de "mayor robustez" sin número.
```

## Dónde escribir

Puede ser:

- Una sección dentro del Estado del Arte (`\section{Trabajos Anteriores Referentes}` en `capitulos/2.estado_del_arte.tex`).
- Un fichero independiente (`capitulos/2b.trabajos_relacionados.tex`) incluido con `\input` en el maestro.

Preguntar al usuario cuál prefiere antes de escribir. Default: fichero independiente.

## Qué devolver

- Ruta `.tex`.
- Tabla comparativa (dimensiones y columnas).
- Lista de limitaciones atribuidas a cada trabajo con la línea del paper
  que las sustenta (si están disponibles los resúmenes).
- Lista de referencias PENDIENTES.
