# Commit Plan – SBB-Verspätungsanalyse (M323)

Duo: **Aimen** & **Elias**

## Where we are

| File | Status |
|---|---|
| `data/ist_daten.csv` | ✅ done (26 984 rows, 7 days, 5 stations, sorted by day → station) |
| `v1/main.py` | `lade_daten` done; functions 1–6 and `main()` missing |
| `v2/main.py` | only stubs: `lade_daten`, functions 1–6, `main()` |
| `data/generate_data.py` | stub (the CSV exists, but the script that produces it doesn't) |
| `tests/test_gleicher_output.py` | ⚠️ passes right now only because v1 and v2 both print nothing |

Problems found in the repo:
- `data/ist_daten.csv` line 13 has `ausfall = 0a` instead of `0`
- `__pycache__/*.pyc` and `.DS_Store` are tracked, and there's no `.gitignore`
- The "Mockup" that `main()` refers to isn't in the repo. **The v1 and v2 output must match byte for byte**, so you both need the exact format before you write any output code.

## How we split the work

**Split by function, not by version.** Each of you writes your functions in **both** v1 (imperative) and v2 (functional):

- **Aimen:** setup and contract, `lade_daten` (v2), functions **1–3** (filter → map → reduce per station)
- **Elias:** functions **4–6** (Ausfälle, Maxima, Ranking), `generate_data.py`, golden-output test

Why: each of you writes imperative *and* functional code (that's what M323 grades), and if v1 ≠ v2, the person who owns that section can fix it.
*(Alternative: Aimen does v1 and Elias does v2. It's simpler, but then only one of you writes the functional version.)*

Each output section in `main()` belongs to the person who owns the function behind it, so each of you adds only your own `print` block.

## Workflow

- Work on your own branch: `aimen/<topic>` or `elias/<topic>`. Merge to `main` through a PR, and the other person reviews it.
- Before every push, run `git pull --rebase origin main`, then `python -m unittest discover tests`.
- One commit = one logical step. The messages below are suggestions.

---

## Phase 0 – Aimen (blocking, do this first, about 1 session)

Elias starts Phase 1 only after A3 is on `main`.

### A1 `chore: add .gitignore and untrack build artefacts`
- New `.gitignore`: `__pycache__/`, `*.pyc`, `.DS_Store`, `.venv/`
- `git rm -r --cached v1/__pycache__ tests/__pycache__ .DS_Store`
- **Done when:** `git ls-files` shows no `.pyc` or `.DS_Store`

### A2 `fix(data): correct invalid ausfall value in row 13`
- `data/ist_daten.csv` line 13: `0a` → `0`
- **Done when:** `ausfall` contains only `0` and `1`

### A3 `docs: add output mockup and data contract` ⭐ *decide this together (a 15-minute call)*
New file `docs/contract.md` (or a section in the README) that fixes:

1. **Exact output**: copy the mockup from the assignment into `docs/mockup.txt`, with headers, column widths, decimal places and section order (1: Statistik pro Bahnhof, 2: Ausfälle pro Tag, 3: Max. Verspätung pro Kategorie, 4: Ranking).
2. **Data shapes**:
   - `lade_daten` → `[(tag, [(bahnhof, [halt, ...]), ...]), ...]` (as in v1)
   - flatten helper `alle_halte(tage)` → halt dicts **plus** the keys `"tag"` and `"bahnhof"`
   - after F2: halt also has `"verspaetung"` (float, minutes) and `"puenktlich"` (bool)
   - F3 → `[(bahnhof, avg_verspaetung, quote_prozent), ...]`
3. **Rules**:
   - Verspätung = `ist − soll` in minutes (`soll` has no seconds, `ist` does)
   - Early arrivals: count as negative, or clamp to `0`? Pick one.
   - Pünktlich = Verspätung `< 3` min
   - F4 counts on the **raw** data (cancelled stops have no `ist` time, so don't filter with F1 first)
   - Ranking: quote descending, ties broken by Ø Verspätung ascending, then by name
   - Rounding and format: use `f"{x:.1f}"` in both versions
- **Done when:** both of you have read it and agree (Elias approves the PR)

---

## Phase 1 – in parallel

### 👤 Aimen

| # | Commit message | Files | Content |
|---|---|---|---|
| A4 | `feat(v2): load CSV into 3D structure functionally` | `v2/main.py` | `lade_daten` with no mutation, e.g. `itertools.groupby` (the CSV is already sorted by day → station) + `alle_halte` |
| A5 | `feat(v1): add alle_halte flatten helper` | `v1/main.py` | imperative counterpart to A4's `alle_halte` |
| A6 | `feat(v1): F1 filter driven stops and F2 compute delay` | `v1/main.py` | loops: drop stops with `ausfall` or empty `ist` (627 rows); compute delay and `puenktlich` |
| A7 | `feat(v2): F1 gefahren filter and F2 mit_verspaetung map` | `v2/main.py` | `filter(gefahren, …)`, `map(mit_verspaetung, …)`, return a new dict (`{**halt, ...}`) |
| A8 | `feat(v1): F3 statistics per station` | `v1/main.py` | Ø delay and on-time rate per station with a loop and a dict |
| A9 | `feat(v2): F3 statistik_pro_bahnhof via reduce` | `v2/main.py` | `functools.reduce` into an accumulator, with no mutation |
| A10 | `feat: print section 1 (station statistics) in v1 and v2` | `v1/main.py`, `v2/main.py` | build the `main()` skeleton (header + section 1) per the mockup |
| A11 | `test: unit tests for lade_daten and F1–F3` | `tests/test_funktionen_1_3.py` | small hand-built examples with known results, for v1 and v2 |

### 👤 Elias

| # | Commit message | Files | Content |
|---|---|---|---|
| E1 | `feat(v1): F4 cancellations per day` | `v1/main.py` | count `ausfall` per `betriebstag` on the raw data (374 in total) |
| E2 | `feat(v2): F4 ausfaelle_pro_tag via reduce` | `v2/main.py` | `reduce` over `tage` |
| E3 | `feat(v1): F5 max delay per category` | `v1/main.py` | S / IR / IC / RE, only stops that actually ran |
| E4 | `feat(v2): F5 maxima_pro_kategorie via filter + reduce` | `v2/main.py` | |
| E5 | `feat(v1): F6 ranking stations by punctuality` | `v1/main.py` | sort by the A3 rule (implement it by hand or use `sorted`, but match v2) |
| E6 | `feat(v2): F6 ranking with sorted and key lambda` | `v2/main.py` | `sorted(..., key=lambda s: (-s[2], s[1], s[0]))` |
| E7 | `feat: print sections 2–4 in v1 and v2` | `v1/main.py`, `v2/main.py` | add to `main()` *after* A10 is merged |
| E8 | `test: unit tests for F4–F6` | `tests/test_funktionen_4_6.py` | |
| E9 | `feat(data): implement generate_data reduction script` | `data/generate_data.py` | raw SBB Ist-Daten (opentransportdata.swiss) → filter to 7 days, 5 stations, trains only → write CSV. Check the column names against the downloaded file. The raw file is **not** committed, so add it to `.gitignore`. |

**Until A4–A9 are merged**, Elias can test F5 and F6 with hand-built halt dicts and statistics tuples that follow the A3 contract.

---

## Phase 2 – Integration (together)

| # | Owner | Commit message | Content |
|---|---|---|---|
| E10 | Elias | `test: add golden output test against mockup` | save the final output as `tests/expected_output.txt`; the test checks v1 == v2 == expected and that the output isn't empty, which closes the gap in the current test |
| A12 | Aimen | `docs: finalize README` | how to run, the data source, a short note on imperative vs functional, and who did what |
| — | both | `chore: final cleanup` | remove TODO docstrings, check variable names and docstrings, `python -m unittest discover tests` all green |

Optional, if you have time: `refactor(v2)` to drop the last `for` loops or mutations in v2 (have the other person review it).

---

## Dependency order

```
A1 → A2 → A3 ─┬─ Aimen: A4 → A5 → A6 → A7 → A8 → A9 → A10 → A11 ─┐
              └─ Elias: E1 → E2 → E3 → E4 → E5 → E6 ── E7* → E8 ───┼─ E10 → A12 → cleanup
                         E9 (independent, any time) ────────────────┘
* E7 needs A10 (the main() skeleton)
```

**Count:** Aimen 12 commits · Elias 10 commits · plus the shared cleanup
