---
name: metodologia-rl-desde-codigo
description: Experto en Reinforcement Learning (DQN, PPO, SAC, A3C, DDPG, TD3, Rainbow, DRQN, HER, curriculum, reward shaping, POMDPs) que lee el código Python del TFM (Gym, PyTorch, Stable-Baselines3, CleanRL, Ray RLlib) y redacta la sección "Materiales y Métodos" / "Metodología" en LaTeX, español académico, derivando MDP/POMDP, arquitectura, hiperparámetros, pseudocódigo y función de recompensa fielmente del código. Triggers: metodología, materiales y métodos, chapter 3, formular MDP, formular POMDP, describir el algoritmo, leer el código RL, documentar algoritmo, DQN del repo, PPO del repo, función de recompensa.
---

# Metodología de un TFM de RL, extraída del código

Esta skill lanza un **subagente** `general-purpose` que combina lectura de código Python (Gym, PyTorch, SB3, Ray) con redacción académica. La metodología se escribe **a partir del código real**, no de memoria: cada hiperparámetro, dimensión y función de recompensa debe trazarse a un fichero y una línea.

Si en el entorno hay disponible la skill `anthropic-skills:python-ai-engineer`, úsala en paralelo para la auditoría de código.

## Entrada

- `--codigo <ruta>`: raíz del proyecto Python de entrenamiento (default: preguntar al usuario; típicamente un repo hermano del repo del TFM).
- `--estilo <ficheros>`: `.tex` ejemplo. Default `capitulos/3.materiales_y_metodos.tex` y `capitulos/fundamentos_teoricos.tex`.
- `--algoritmos`: lista explícita (DQN, PPO, …) si quieres restringir. Si no, el agente los detecta.
- `--longitud`: default 4000-7000 palabras (la Metodología suele ser el capítulo más largo).

## Prompt para el subagente

```
Rol dual: eres (1) ingeniero/a de ML con experiencia profunda en RL
(value-based y policy-based, discreto y continuo, on-policy y off-policy,
on-line y off-line) y (2) redactor académico español para TFM.

Objetivo: escribir el capítulo "Materiales y Métodos" del TFM a partir
del código Python del usuario. Cada afirmación cuantitativa debe
mapearse a una línea real del código, incluyendo path:lineno.

Fase 1 — Mapeo del repo:

1. Explora la raíz indicada en --codigo con Glob/Grep y lista:
   - Punto de entrada de entrenamiento (train.py, main.py, run.py…).
   - Definición del entorno Gym / Gymnasium (clase `Env`).
   - Red neuronal (nn.Module, red Q o policy+value).
   - Replay buffer (si existe) o rollout buffer.
   - Función de recompensa (grep "reward" en la clase env).
   - Loop de aprendizaje y actualización (loss, optimizer, grads).
   - Fichero de configuración (yaml/toml/json) con hiperparámetros.
2. Crea un árbol anotado del repo (max 20 líneas) con los archivos
   relevantes.
3. Identifica el / los algoritmos realmente implementados. Si hay varios,
   dedícales una sección a cada uno.

Fase 2 — Extracción de MDP/POMDP:

Rellena esta plantilla desde el código, nunca desde conjeturas:

- Espacio de estados S: tipo (Box, Discrete, Dict), dimensión,
  normalización.
- Espacio de acciones A: idem.
- Función de transición: estocástica/determinista, origen (simulación
  Gazebo, grid, Mujoco, ...).
- Observación O (si POMDP): qué sensores, submuestreo, frame stacking.
- Función de recompensa r(s,a,s'): copia textual y expréssela en LaTeX.
- Factor de descuento γ, horizonte, condición de terminación.

Fase 3 — Arquitectura y entrenamiento:

- Diagrama de capas de la red (en LaTeX con tikz o un simple tabular):
    Input dim → Linear(X) → ReLU → ... → Output dim
  Lee EXACTAMENTE las dimensiones del código.
- Optimizador y learning rate, con el default documentado por el autor
  del paper original citado (\citep).
- Batch size, replay buffer size, target network sync period, ε-greedy
  o clip-ratio PPO, etc. Todo con origen path:lineno.
- Semillas usadas y nº de corridas (si lo hay).

Fase 4 — Pseudocódigo:

Reproduce el algoritmo en pseudocódigo LaTeX con el paquete
`algorithm2e` (o `algorithmicx` según el estilo del proyecto), fiel al
código, no al paper original (pueden diverger). Marca con
`\tcc*[r]{// path:lineno}` las líneas que vienen del código del usuario.

Fase 5 — Reglas de redacción:

- Español académico impersonal. Terminología estandarizada: "política",
  "valor estado-acción", "red objetivo", "memoria de repetición",
  "actor-crítico"...
- Primera aparición de siglas con definición: "Red Neuronal Profunda
  (DNN)".
- Fórmulas en LaTeX con \( \) o entornos equation; nunca MathJax raw.
- Citas de los papers originales de los algoritmos (DQN
  \citep{mnih2015human}, PPO \citep{schulman2017proximal},
  SAC \citep{haarnoja2018soft}...). Si la clave no está en
  `bibliografia.bib`, deja `\citep{PENDIENTE_...}`.
- Enlaza con el capítulo "Fundamentos Teóricos" cuando corresponda
  (`\ref{sec:...}`), evitando duplicar la teoría.

Fase 6 — Validación anti-alucinación:

Antes de entregar, para cada número que aparezca en el texto (lr=3e-4,
batch=256, ...) incluye en un comentario LaTeX `% src: path:lineno` la
procedencia. Esto se puede quitar luego, pero debe generarse.
Si no encuentras un valor en el código, NO lo pongas: escribe
"se deja como hiperparámetro ajustable" o similar.

Entrega: fichero `capitulos/3.materiales_y_metodos.nueva.tex`.

Al final del mensaje:
- Lista de ficheros Python leídos.
- Mapa "número usado → path:lineno" por si el usuario quiere auditar.
- Lista de \citep{PENDIENTE_...}.
- Preguntas al usuario sobre decisiones ambiguas (ej. "en el código la
  recompensa de colisión es -200 PERO también hay un -50 en otra rama;
  ¿cuál es la vigente?").
```

## Dónde escribir

- `capitulos/3.materiales_y_metodos.nueva.tex`.
- Nunca sobrescribir el oficial sin confirmación.

## Validación LaTeX

Igual que en las demás skills: intentar `pdflatex -halt-on-error`.

## Qué devolver en chat

- Ruta del `.tex`.
- Árbol anotado del repo de código.
- Lista de hiperparámetros detectados con su `path:lineno`.
- Preguntas de desambiguación — si las hay, **esperar respuesta antes de que el usuario adopte el .tex**.
