# Context — `app/analysis/`

> **UA:** Аналіз: рахує метрики з лем (частота, тональність, тема).
>
> Computes metrics from preprocessed lemmas. Pure functions — lemmas in,
> metrics out. No DB, no spaCy model, no HTTP.
> **Status:** Stage 6 ✅ done.

## Purpose

Turn the lemma list from `app.preprocessing.preprocess()` into the numbers we
store and show: top words, a sentiment label/score, and a topic.

## Key files

| File | Function | Returns |
|------|----------|---------|
| `frequency.py` | `word_frequencies(lemmas, top_n=None)` | `list[(word, count)]`, most frequent first |
| `sentiment.py` | `analyze_sentiment(lemmas)` | `SentimentResult(label, score)` |
| `topic_detection.py` | `detect_topic(lemmas)` | topic string, or `"інше"` |
| `__init__.py` | exports the three above + word lists | — |

## How each works (kept simple on purpose)

- **Frequency:** `collections.Counter` over the lemmas.
- **Sentiment:** dictionary method — count words in `POSITIVE_WORDS` vs
  `NEGATIVE_WORDS`; `score = (pos - neg) / (pos + neg)` in [-1, 1];
  `neutral` + `0.0` when no sentiment words appear. No machine learning.
- **Topic:** count how many lemmas fall in each topic's keyword set in
  `TOPIC_KEYWORDS`; the highest count wins, ties keep the earlier topic,
  no hits → `"інше"`.

## Usage

```python
from app.preprocessing import preprocess
from app.analysis import word_frequencies, analyze_sentiment, detect_topic

lemmas = preprocess(article.raw_content)
word_frequencies(lemmas, top_n=10)   # -> [('україна', 5), ...]
analyze_sentiment(lemmas)            # -> SentimentResult(label='negative', score=-0.5)
detect_topic(lemmas)                 # -> 'війна'
```

## Design decisions / limits

- **Transparent, not accurate-at-all-costs.** Word-list sentiment is naive (it
  flags a piece on "Death of a Salesman" negative via «смерть») — fine for an
  educational project; the logic is readable and easy to extend.
- Word lists / keyword sets are **lemmas**, matching preprocessing output.
- Extend by editing the sets in `sentiment.py` / `topic_detection.py`.

## Tested by

`tests/test_analysis.py` — frequency order + top_n, positive/negative/neutral
sentiment, topic match + fallback. Pure data, runs without the model.

## Next that touches this layer

Stage 7 — `PipelineService` calls these per article and saves the results into
`AnalysisResult` (sentiment, topic, word_count) and `WordFrequency` rows.
