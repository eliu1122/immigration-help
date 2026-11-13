# Step 1: source list

**Built:** `sources.yaml` (24 sources), `scripts/check_sources.py`, report in
`sources_check.md`.

**Check:** every URL is fetched live. It must return 200, and the fetched page
(HTML text, or the first 3 pages of a PDF) must contain the entry's `expect` text, so
a redirect to an unrelated page fails. For Policy Manual parts the part page must
also link at least one chapter.

## Result: 17/24 confirmed, 7 blocked

- **Confirmed (USCIS):** 5 form-instruction PDFs (I-130, I-485, I-864, I-765, I-131),
  their 5 form pages, the fee schedule (G-1055), the Visa Bulletin filing charts page,
  and 5 Policy Manual parts: Vol 1 Part E (9 chapters), Vol 6 Part B (7),
  Vol 7 Part A (11), Vol 7 Part B (8), Vol 10 Part A (4).
- **Blocked (State Department):** all 7 travel.state.gov URLs return HTTP 403 to the
  script and to Claude's WebFetch tool. This looks like a block on non-browser
  clients, not wrong URLs, but **these URLs are not confirmed**: I wrote them from
  memory. They are marked `verified: false`. I did not try to get around the block
  by spoofing a browser.

## Changed during the step

The first draft listed one chapter per Policy Manual part. Each "Chapter 1" turned out
to be "Purpose and Background" only, so the entries are now whole parts, and step 2
will fetch every chapter a part page links to.

## Not checked / open

- The 7 State Department URLs: Eric to open each in a browser. Step 2 needs a way to
  get these pages: a manual save, or another official source for the same content.
- Vol 7 Part D (Family-Based Adjustment) loads, but no chapter links matched the
  pattern the other parts use. It may be split into sub-parts. Left out for now.
- Vol 1 Part E has no chapter 7 link, and Vol 10 Part A no chapter 3. Possibly
  reserved; not checked.
- Not yet in the list: USCIS case status message meanings, processing times
  (egov.uscis.gov is a JS app), the I-130A, 9 FAM.
- Set completeness: whether these are the *right* sources for v1 is Eric's review.
