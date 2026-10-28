---
name: buscar-articulos-scholar
description: Buscar artículos científicos en Internet (scholar.google.com, arXiv, Semantic Scholar) sobre un tema para el TFM. Admite filtros por fecha, autor, revista y ordenación por fecha o relevancia. Devuelve lista estructurada con título, autores, año, revista/venue, resumen breve, cita en BibTeX cuando sea posible y enlace. Triggers: buscar en scholar, buscar artículos, Google Scholar, scholar.google.com, bibliografía, encontrar papers, literatura científica, revisión bibliográfica, buscar referencias, state of the art search.
---

# Buscar artículos científicos (Google Scholar + fuentes abiertas)

Esta skill lanza un **subagente** `general-purpose` que investiga el tema pedido con WebFetch/WebSearch. Google Scholar bloquea bots agresivamente; el agente debe tener fuentes de respaldo.

## Cómo invocarla

Cuando el usuario pida buscar artículos, lanza un agente con este contrato de prompt. **Nunca** intentes la búsqueda tú directamente turno a turno: delega al agente para no llenar tu contexto con HTML crudo.

### Prompt base para el agente

```
Investiga artículos científicos sobre: <TEMA>.

Filtros solicitados (si el usuario no los menciona, usa los por defecto):
- Rango de fechas: <AÑO_MIN>–<AÑO_MAX>  (por defecto: últimos 5 años)
- Autores de interés: <LISTA o "cualquiera">
- Revista/venue: <LISTA o "cualquiera">
- Orden: <relevancia | fecha descendente>  (por defecto: relevancia)
- Idioma: <es | en | cualquiera>  (por defecto: cualquiera)
- Nº objetivo de resultados: <N>  (por defecto: 15)

Fuentes a consultar, en este orden:
1. Google Scholar (scholar.google.com) con la query construida, usando los parámetros
   `as_ylo` (año desde), `as_yhi` (año hasta) y `scisbd=1` para orden cronológico.
   Si Scholar devuelve CAPTCHA o 429, cae en silencio a la siguiente fuente.
2. arXiv.org (api.arxiv.org/api/query) — ideal para preprints de ML/RL.
3. Semantic Scholar (api.semanticscholar.org/graph/v1/paper/search) — tiene API JSON
   libre y entrega abstracts, DOIs y citas.
4. DBLP, OpenAlex o CORE si lo anterior resulta insuficiente.

Para cada artículo que incluyas en la lista final valida:
- Que el título y los autores concuerdan en al menos dos fuentes O en la fuente oficial
  (editorial / arXiv), para no inventar referencias.
- Que el enlace resuelve a una página real (comprueba el status HTTP si WebFetch lo
  permite). Prefiere el DOI o el abstract oficial sobre un PDF pirata.

Devuelve un **informe en Markdown en español** con esta estructura exacta:

## Resumen de la búsqueda
- Query usada: `...`
- Fuentes consultadas: ...
- Nº total encontrados / Nº incluidos: X / Y

## Resultados

### [N] Título del artículo
- **Autores:** ...
- **Año / Venue:** 2024 / IEEE T-RO
- **Idea principal (1-2 frases):** ...
- **Relevancia para el TFM (RL + navegación map-less de AGVs):** alta/media/baja — por qué
- **DOI / Enlace:** ...
- **BibTeX:**
  ```bibtex
  @article{claveCorta2024,
    ...
  }
  ```

## Lagunas detectadas
Qué subtemas quedan poco cubiertos en la literatura reciente.

Reporta en menos de ~1200 palabras. Si una referencia no cumple la validación anti-
alucinación, exclúyela y dilo en "Resumen".
```

### Launcher recomendado

Lanza el agente con `subagent_type: "general-purpose"` y `run_in_background: false` si el siguiente paso depende del resultado (p. ej., inmediatamente añadir a `bibliografia.bib`); en caso contrario, en background.

## Añadir al proyecto

Las entradas BibTeX finales van a `bibliografia.bib` (fichero ya existente). Antes de añadir, comprueba que la clave no colisione:

```bash
grep -E '^@[a-zA-Z]+\{clave,' "C:/Users/marti/Documents/Studies/Masters/Control UCM/TFM/Documento_TFM/bibliografia.bib"
```

Si el usuario pide "solo buscar sin añadir", respétalo.

## Notas sobre Google Scholar

- `start=0,10,20...` pagina.
- `as_sdt=0,5` restringe a artículos (sin patentes).
- `hl=es` fuerza interfaz en español, útil para parsing.
- Si aparece "unusual traffic from your computer network", el agente **no debe reintentar en bucle**: anota el bloqueo y pasa a arXiv/Semantic Scholar.

## Qué devolver al usuario

Un resumen de 3-5 líneas con los nombres y años de los top-5 resultados, y la ruta donde el agente dejó el informe completo (en `scratchpad/` si procede).
