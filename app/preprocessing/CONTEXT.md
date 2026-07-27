# Context — `app/preprocessing/`

> **UA:** Препроцесинг: перетворює сирий текст на чисті слова/леми.
>
> Turns raw article text into clean tokens/lemmas. Pure functions only —
> text in, text out. No DB, no HTTP.
> **Status:** Stage 5 ✅ done.

## Purpose

Prepare text for analysis (Stage 6): remove HTML, split into words, drop
stopwords, reduce words to base forms (lemmas).

## Key files

| File | Function | Needs spaCy? |
|------|----------|--------------|
| `cleaner.py` | `clean_text(raw)` — strip HTML, collapse whitespace | no |
| `tokenizer.py` | `tokenize(text)` — regex word split, lowercase | no |
| `stopwords.py` | `STOPWORDS`, `remove_stopwords(tokens)` | spaCy pkg only* |
| `lemmatizer.py` | `get_nlp()`, `lemmatize(text)` — base forms | **yes (model)** |
| `__init__.py` | `preprocess(raw)` — full pipeline | yes (model) |

\* `stopwords` reads spaCy's Ukrainian word list; it does **not** need the model
download, only the `spacy` package.

## Two paths (by design)/ два шляхи

- **Lemma path (main):** `preprocess(raw)` = `clean_text` → `lemmatize` (spaCy
  `uk_core_news_sm`) → stopwords dropped. Best for analysis (`новини`→`новина`).
- **Lightweight path:** `tokenize` + `remove_stopwords` — fast, no model, surface
  words only. Handy for quick counts or model-free tests.

## Usage

```python
from app.preprocessing import preprocess, clean_text

clean_text("<p>Це <b>новини</b>!</p>")   # -> "Це новини !"
preprocess("<p>Це нові новини про Київ</p>")
# -> ['новий', 'новина', 'київ']   (cleaned, lemmatized, stopwords removed)
```

## Design decisions

- **Pure functions** — no side effects. Storing `cleaned_content` is the
  pipeline/repository's job (Stage 7), not here (architecture rule 2).
- spaCy model is loaded **once** via `functools.lru_cache` in `get_nlp()` —
  loading it is slow, so we never reload.
- Lemmatizer keeps only alphabetic tokens and uses spaCy's `is_stop` so stopword
  removal matches the base forms accurately.

## Tested by

`tests/test_preprocessing.py` — cleaner/tokenizer/stopwords always run;
lemmatizer/preprocess tests **skip automatically** if `uk_core_news_sm` is not
installed (`spacy.util.is_package`).

## Dependencies

`spacy` + `uk_core_news_sm` (+ auto `pymorphy3`, dicts). See
`docs/DEPENDENCIES.md`.

## Next that touches this layer

Stage 6 — analysis modules consume `preprocess()` output: word frequency,
sentiment, topic keywords.
