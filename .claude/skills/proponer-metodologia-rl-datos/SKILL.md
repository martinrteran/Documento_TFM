---
name: proponer-metodologia-rl-datos
description: Experto en RL que PROPONE nuevas metodologías o mejoras concretas sobre la metodología actual del TFM, justificadas con datos reales (logs de entrenamiento, curvas de retorno, matrices de confusión, estadísticos del entorno) y fundamentadas en literatura verificable. Nunca propone cambios "por intuición": cada propuesta nace de una métrica observada + un paper que respalda la mejora + un plan experimental para validarla. Triggers: proponer metodología, mejorar algoritmo, qué puedo cambiar, próximos pasos RL, ablation, nuevo baseline, sugerir enfoque, metodología alternativa, data-driven.
---

# Proponer metodologías RL fundamentadas en datos

Es la hermana mayor de `metodologia-rl-desde-codigo`. Allí se documenta lo que **existe**; aquí se propone lo que **podría mejorarlo**, siempre justificado con:

- Datos del propio experimento (logs, curvas, métricas).
- Un trabajo publicado que respalde el cambio.
- Un plan experimental para medir si el cambio funciona (ablation, baseline, semillas).

**Nunca** proponer "prueba con lr=1e-3 a ver" sin fundamento. Esta skill rechaza el consejo tipo barra de bar.

## Entrada

- `--codigo`: raíz del repo Python (igual que la skill hermana).
- `--logs <ruta>`: fuente de datos reales. Admite:
  - CSVs de Stable-Baselines3 (`progress.csv`), CleanRL (`runs/*/events.out*`),
    Ray RLlib (`result.json`), TensorBoard event files.
  - WandB / MLflow export si está disponible.
  - Un fichero `metrics.json` propio.
- `--max_propuestas`: default 5.
- `--presupuesto`: compute realista (horas GPU, nº semillas). Guía qué propuestas son viables.

## Prompt para el subagente

```
Rol: investigador/a senior en RL con reflejo crítico anti-"folk tuning".
Rechazas sugerencias sin datos y sin referencia.

Objetivo: proponer <max_propuestas> mejoras sobre la metodología actual
del TFM, cada una justificada por (1) un dato real observado, (2) una
cita bibliográfica y (3) un plan experimental concreto para medir el
impacto.

Fase 1 — Diagnóstico de datos reales:

1. Carga los logs de --logs en un DataFrame (pandas). Ten en cuenta
   formatos típicos:
    - `progress.csv` (SB3): columnas rollout/ep_rew_mean, train/loss,
      etc.
    - TensorBoard: usa `tensorboard.backend.event_processing` para
      extraer scalars sin arrancar el servidor.
    - RLlib: `result.json` por iteración.
2. Si hay varias corridas / semillas, agrúpalas y calcula media + IQM
   (interquartile mean, recomendado por Agarwal et al. 2021
   \citep{agarwal2021deep}) y bandas de confianza.
3. Produce 4-6 gráficas en `scratchpad/figs_diag/`:
    - Retorno medio por episodio vs. pasos.
    - Longitud de episodio vs. pasos.
    - Tasa de éxito (si existe) vs. pasos.
    - Pérdida de valor / política vs. pasos.
    - Si procede: entropía, KL (PPO), ε (DQN).
4. Detecta patologías con criterios objetivos:
    - **Varianza alta entre semillas** (IQR / mediana > 0.5) → ruido alto.
    - **Saturación temprana** (meseta antes del 30 % del presupuesto).
    - **Policy collapse** (entropía → 0 muy pronto en PPO/SAC).
    - **Catastrophic forgetting** (retorno baja tras subir).
    - **Reward hacking** (longitud baja y retorno alto sin éxito).
    - **Overestimation** (Q-values crecen monótonamente).

Fase 2 — Propuestas (una ficha por propuesta):

Plantilla OBLIGATORIA por propuesta — rechazar la propuesta si falta
alguna de las tres patas:

### Propuesta N — <nombre corto>
- **Síntoma observado (datos):** "La curva de retorno medio satura en
  600 pasos ×10⁵ a 0.42 con IQR 0.18, mientras que la de éxito se
  estanca en 0.55 (ver `figs_diag/retorno.png` y `exito.png`)."
- **Hipótesis causal:** "Patología X por motivo Y."
- **Intervención concreta:**
  - Cambio en el código (indica path:lineno).
  - Hiperparámetro, pérdida, arquitectura o pipeline afectado.
- **Fundamento bibliográfico:** cita \citep{clave}. Debe ser un paper
  cuya metodología ataca la MISMA patología; **no vale citar el paper
  del algoritmo base**. Si no encuentras una cita adecuada, usa la
  skill `buscar-articulos-scholar` o declara "sin respaldo publicado
  encontrado — no se propone".
- **Riesgo / posible efecto adverso:** 1-2 frases.
- **Plan experimental:**
  - Baseline: la configuración actual.
  - Variante: la propuesta.
  - Semillas mínimas: 5 (regla de IQM / rliable).
  - Métrica primaria: ...
  - Criterio de éxito: ej. "IQM del retorno sube ≥ 0.1 con intervalo
    de confianza bootstrap que excluye 0".
  - Presupuesto estimado: X horas GPU.
- **Coste de ingeniería:** bajo / medio / alto (líneas tocadas aprox.).

Fase 3 — Priorización:

Ordena las propuestas por *expected value* = (probabilidad de que
funcione · magnitud del beneficio) / coste. Explica el criterio para
cada posición.

Fase 4 — Salida LaTeX:

Añade al final del mensaje un bloque `.tex` listo para pegar en el
capítulo "Metodología" como subsección "Propuestas de mejora
metodológica fundamentadas en datos", con las fichas convertidas a
prosa académica + una tabla resumen (técnica, patología, cita,
coste, prioridad).

Reglas duras:

- Está PROHIBIDO proponer sin dato observable que lo motive. Si los
  logs no muestran la patología, decirlo explícitamente ("no se
  propone X porque los datos actuales no evidencian la patología que
  justificaría X").
- Está PROHIBIDO proponer cambios que requieran > --presupuesto GPU.
- Está PROHIBIDO citar un paper que no se haya leído: usa la skill
  `resumir-articulos-cientificos` si hace falta.
- No prometer mejoras numéricas concretas antes de medir ("sube el
  retorno un 20 %" NO).
```

## Fuentes de respaldo típicas (sin memorizar — verificar)

Para que el agente no cite de memoria, estas son líneas de investigación donde buscar según la patología:

- Varianza entre semillas → *rliable* (Agarwal et al. 2021), *deep RL that matters* (Henderson et al. 2018).
- Policy collapse PPO → *target KL*, entropy regularisation, PPO-penalty.
- Overestimation DQN → Double DQN, Dueling, Clipped Double Q, QR-DQN, C51.
- Sample inefficiency → prioritized replay, HER, model-based (Dreamer, MuZero), curriculum.
- Reward hacking → reward shaping con potenciales (Ng 1999), inverse RL.
- Exploración pobre → RND, NGU, parameter noise, intrinsic motivation.

**El agente debe buscar la cita real antes de poner la clave BibTeX, no asumir que existe.**

## Qué devolver en chat

- Diagnóstico en 5-8 bullets con las patologías realmente observadas.
- Lista ordenada de propuestas con prioridad.
- Ruta al `.tex` con la subsección redactada.
- Ruta de las gráficas diagnósticas.
- Preguntas abiertas al usuario sobre decisiones de diseño que afectan al experimento.
