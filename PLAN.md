# Caseline build plan

Grounded answers about US immigration cases, built only from official USCIS and
State Department guidance. PRD: `about-me/caseline-prd.html`. Pipeline is ported
from `SEC Simplifier/sec-simplifier`.

## Rules for every step

1. No immigration fact enters code, tests or the eval set from memory. It must come
   from a source that was actually fetched, and quotes are verified by script.
   Anything not verified is marked `UNVERIFIED`.
2. One step at a time. Before starting: state what will be built and how it will be
   checked. After: run the checks, write a worklog entry (`worklog/YYYY-MM-DD-step-N-*.md`:
   what was checked, what wasn't, open doubts), tick the boxes here, commit on a branch.
3. Eric reviews each step before the next one starts. A step is only `[x]` when its
   own checks pass; Eric's review is ticked separately.

## Steps

### 0. Scaffold
- [ ] Repo layout, README, requirements, `worklog/`
- [ ] Port source-independent sec-simplifier code: chunk IDs, quote verification, scoring harness
- [ ] Check: `pytest` passes on ported tests; nothing fetched from the web
- [ ] Reviewed by Eric

### 1. Source list
- [x] `sources.yaml`: exact official URLs for v1 (I-130, I-485, I-864, I-765, I-131 instructions; Policy Manual parts for those forms; NVC/CEAC help pages; 221(g) / administrative processing; Visa Bulletin; USCIS fee schedule)
- [ ] Every URL loaded live and confirmed (status, content type, page title) by `scripts/check_sources.py`; no guessed URLs
      — 17/24 confirmed; 7 travel.state.gov URLs blocked (HTTP 403), `verified: false`, need a browser check
- [ ] Check: `sources_check.md` report, all rows OK — blocked by the same 7
- [ ] Reviewed by Eric: is this the right set?

### 2. Ingest
- [ ] Fetch every source with a generic client name; save raw HTML/PDF with fetch date and content hash
- [ ] Text extraction for PDF form instructions
- [ ] Check: manifest of everything saved; side-by-side spot checks of extracted text vs. the live page
- [ ] Reviewed by Eric

### 3. Chunking
- [ ] Section-aware chunking for Policy Manual HTML and PDF instructions
- [ ] Fee schedule and Visa Bulletin tables read as tables
- [ ] Every chunk has a stable ID, source URL, section and fetch date
- [ ] Check: tests pass; printed sample chunks from each source type
- [ ] Reviewed by Eric

### 4. Index and retrieval
- [ ] Port the Chroma store and hybrid search
- [ ] Check: probe questions with their top retrieved passages (retrieval only, no answers)
- [ ] Reviewed by Eric

### 5. Eval set
- [ ] 30-50 cases written only from saved text; a script confirms every expected quote exists in its source
- [ ] About a third are should-decline: case-outcome predictions, out-of-source questions, legal advice
- [ ] Reviewed by Eric, every case (the most important review)

### 6. Generation
- [ ] Port `generate.py`: quote verification, "not covered" abstention
- [ ] Wording guard against legal advice; pasted status-line input
- [ ] Check: answers to eval questions, every quote machine-checked
- [ ] Reviewed by Eric

### 7. Evaluate and tune
- [ ] First baseline scored and saved
- [ ] Tune the retrieval distance floor for declining
- [ ] Check: score report vs. baseline
- [ ] Reviewed by Eric

### 8. Freshness
- [ ] Scheduled re-fetch; answers built from stale pages are flagged
- [ ] Check: test with a faked old fetch date gets flagged
- [ ] Reviewed by Eric

### 9. UI
- [ ] Port the sec-simplifier app
- [ ] Check: run it and try it
- [ ] Reviewed by Eric
