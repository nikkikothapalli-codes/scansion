# Scansion

Paste a poem, get its metre, every foot that departs from it, the rhyme scheme,
and where to breathe when reading it aloud.

Built for performance rather than analysis, based on my own experiences as a 2025 Foyle Young Poet of the Year, a National High School Poetry Quarterly Contest winner, and a University Interscholastic League Regional Qualifier in Poetry. I am also an eight-time finalist in Poetry Interpretation and 2x Speech Captain + District Coach. 

Most scansion tools tell you a line is iambic pentameter. What a performer needs to know is which foot inverts and where the caesura falls, because those are the places the reading changes.

```
 ˘   ⁄  │ ˘   ⁄  │  ⁄   ˘ │ ˘  ˘ │  ⁄    ⁄
Shall I │ com pare │ thee to │ a sum │ mer's day?
 iamb      iamb       trochee  pyrrhic   spondee
```

## Running it

Two processes, two terminals.

```bash
cd api
pip install -r requirements.txt
uvicorn api:app --reload
```

```bash
cd web
npm install
npm run dev
```

Open http://localhost:5173. If the API isn't running the page falls back to
bundled sample data and says so, so the frontend demonstrates itself either way.

```bash
cd api && pytest        # 29 tests
```

## Layout

```
api/
  scansion.py        the engine — dictionary, demotion, metre, rhyme
  api.py             FastAPI wrapper
  test_scansion.py   29 tests pinned to lines whose scansion isn't disputed
web/
  src/Scansion.jsx   the interface
```

## How it reads a line

```
text
  ↓  CMUdict lookup         phonemes → syllable count + stress digits
  ↓  OOV fallback           orthographic estimate, flagged uncertain
  ↓  function-word demotion word stress → line stress
  ↓  template matching      best-fitting metre
  ↓  foot comparison        substitutions
  ↓  performance layer      what to do out loud
```

## Decisions

**Word stress is not line stress.** CMUdict records words in isolation, so every
monosyllabic function word comes back stressed — "the", "of", "and". Read
naively, every line over-reports its beats. A demotion pass drops them, then
reverts any demotion that would leave three unstressed syllables in a row, which
English resists.

Getting the revert right was the hardest part. The first version looked only at
the middle syllable of each `000` run and gave up if that word wasn't
revertible — silently leaving in place the exact pattern the pass existed to
remove. It now tries every demoted word inside the run. Two tests cover it.

**Three stress levels collapse to two.** CMUdict marks primary, secondary and
unstressed. Verse has beat and no-beat, and secondary stress reads as a beat in
a metrical line.

**Ambiguous pronunciations are kept, not resolved.** "Fire" is one syllable or
two depending on the reader, and poets exploit that to make lines scan. Both are
preserved rather than taking the first and hoping.

**Out-of-vocabulary words are flagged, not hidden.** Poetry is full of archaic
diction and coinages. Stress for these is guessed from suffix patterns mined out
of CMUdict at import — grouping words by ending and taking the modal stress
pattern — and the result is marked uncertain so the interface can show a dotted
underline instead of projecting false confidence.

**Metre confidence is reported.** A 60% match means the line is loose. That's
information a reader wants, not a failure to hide.

**Syllable splitting in the UI is display-only.** Feet are conventionally shown
divided across word boundaries (`com │ pare`), so the frontend chops each word
into as many pieces as the dictionary says it has syllables. That split is
orthographic guessing and occasionally lands in the wrong place; the stress data
underneath it is dictionary-accurate.

## Known limits

- Assumes English and a standard accent.
- Free verse gets a low-confidence match rather than being identified as free verse.
- Caesura detection keys on punctuation, so it misses unpunctuated pauses.
- Accentual-syllabic metre only — no syllabic forms like haiku.
- The frontend assumes two-syllable feet when drawing foot divisions.
