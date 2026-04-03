# Pipeline Profiling: 2512.13961 (OLMo 3)

**Date:** 2026-04-02
**Paper:** OLMo 3 — 117 pages, 55 tables, 43 figures, 27 equations
**Final output:** `papers/llm/pretraining/olmo-3.md` (76,983 bytes)

---

## 1. Stage Breakdown

| Stage | Duration (s) | Tokens | Tool Uses | Output (bytes) | Status |
|-------|-------------|--------|-----------|----------------|--------|
| Download | ~3 | — | 1 | 6.5 MB PDF | OK |
| Extract | ~5 | — | 1 | text.txt + registry | OK |
| **Extractor** | **857** | **16,595** | **43** | **43,734** | 25% coverage |
| **Extractor Retry** | **695** | **154,708** | **76** | **+26,364 → 70,098** | Supplemented |
| **Writer-visual** | **642** | **108,478** | **26** | **43,069** | Bottleneck |
| **Writer-text-0** | **194** | **70,887** | **16** | **12,040** | OK |
| **Writer-text-1** | **182** | **72,401** | **25** | **8,452** | OK |
| Merge | ~2 | — | 1 | 39,589 chars | OK |
| Gates R1 | ~3 | — | 1 | — | Failed: H2,H4,H5,H8 |
| **Fixer** | **352** | **98,097** | **22** | **0 delta** | Bug: no-op |
| Gates R2 | ~3 | — | 1 | — | Same failures |
| Classify + Save | ~2 | — | 2 | 76,983 | OK |

## 2. Totals

| Metric | Value |
|--------|-------|
| Total critical path wall-clock | ~2,563s (**~43 min**) |
| Total agent tokens | **521,166** |
| Total agent cumulative duration | 2,922s (parallel writers overlap) |
| Total tool uses | 208 |
| Final output size | 76,983 bytes |
| Intermediate notes size | 70,098 bytes |

## 3. Critical Path

```
Download (3s)
  → Extract (5s)
    → Extractor (857s)
      → Extractor-retry (695s)
        → Writers parallel [max 642s]
          → Merge (2s)
            → Gates R1 (3s)
              → Fixer (352s)
                → Gates R2 (3s)
                  → Classify+Save (2s)

Total: ~2,563s (~43 min)
```

## 4. Token Efficiency

| Component | Tokens | Output (bytes) | Tokens/Byte | Efficiency |
|-----------|--------|----------------|-------------|------------|
| Extractor (initial) | 16,595 | 43,734 | 0.38 | Excellent |
| Extractor (retry) | 154,708 | 26,364 | 5.87 | Poor — re-read overlap |
| Writer-visual | 108,478 | 43,069 | 2.52 | Moderate |
| Writer-text-0 | 70,887 | 12,040 | 5.89 | Poor — large notes input |
| Writer-text-1 | 72,401 | 8,452 | 8.57 | Poor — large notes input |
| Fixer | 98,097 | 0 | ∞ | **Wasted** |

## 5. Bottleneck Analysis

### B1: Extractor coverage on long papers (Priority: HIGH)

- **Problem:** Initial extractor only achieved 25% page coverage on 117 pages, triggering a full retry round
- **Impact:** 695s + 154K tokens wasted on retry
- **Root cause:** Extractor reads text.txt in chunks but stops too early for very long papers
- **Proposed fix:**
  - For papers > 80 pages, instruct extractor to split into 2 parallel sub-agents (pages 1–60, pages 61+)
  - Or: pre-split text.txt by page range and assign each to a separate extractor
- **Expected savings:** Eliminate retry entirely → save ~695s and ~155K tokens

### B2: Writer-visual 3x slower than text writers (Priority: MEDIUM)

- **Problem:** writer-visual took 642s vs 194s/182s for text writers
- **Impact:** Dominates the parallel writer stage wall-clock
- **Root cause:** Heavier quality contract (≥6 tables, pseudocode, numerical derivation, flow diagrams)
- **Proposed fix:**
  - Split writer-visual into 2 sub-writers: `writer-method` (方法详解) and `writer-experiment` (实验与归因)
  - This would bring max writer time down to ~320s
- **Expected savings:** ~300s on critical path

### B3: Fixer no-op (Priority: HIGH)

- **Problem:** Fixer consumed 352s and 98K tokens but produced output identical to input
- **Impact:** Pure waste — 352s + 98K tokens
- **Root cause:** Agent reported making changes but actually wrote the same content (or wrote to wrong path)
- **Proposed fix:**
  - Add post-fixer `diff` check: if merged.md == merged_fixed.md, skip gates R2
  - Investigate agent write path — may need explicit `cp merged.md merged_fixed.md` before handing to fixer, then verify diff after
  - Consider giving fixer an Edit-only strategy instead of full file rewrite
- **Expected savings:** 352s + 98K tokens when fixer produces no changes

### B4: Gate thresholds don't scale for long papers (Priority: MEDIUM)

- **Problem:** H2 (subsection coverage), H4 (table count=55), H8 (number tracing) all fail systematically for 117-page papers
- **Details:**
  - H2: coverage=0.0014 — registry parses table cell numbers as "subsections", inflating the denominator
  - H4: requires 55 tables (= paper's total) — analysis realistically includes ~20 key tables
  - H8: 1,036/1,036 numbers untraced — registry matching appears broken
- **Proposed fix:**
  - H4: `required = min(paper_tables, 20)` or scale as `max(6, paper_tables * 0.3)`
  - H2: Filter out numeric "subsections" from registry before computing coverage
  - H8: Debug the tracing algorithm — 100% untraced suggests a format mismatch, not actual data issues
- **Expected savings:** Avoids unnecessary fixer rounds on long papers

## 6. Optimization Roadmap

| Priority | Fix | Time Saved | Tokens Saved | Effort |
|----------|-----|-----------|--------------|--------|
| P0 | Parallel extractor for long papers | ~695s | ~155K | Medium |
| P0 | Fixer no-op detection | ~352s | ~98K | Low |
| P1 | Split writer-visual into 2 | ~300s | ~30K | Medium |
| P1 | Scale gate thresholds by paper size | Avoids fixer | ~98K | Low |
| P2 | Reduce notes.md input for text writers | — | ~40K | Low |

**Best-case optimized critical path:**
```
Download (3s) → Extract (5s) → Extractor-parallel (500s) → Writers-4-way (320s) → Merge+Gates (5s) → Save (2s)
Total: ~835s (~14 min) — a 3x speedup from current 43 min
```
