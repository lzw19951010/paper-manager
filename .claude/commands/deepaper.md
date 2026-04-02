<!-- deepaper-version: 2 -->
Analyze an arxiv paper and save to the deepaper knowledge base using a multi-agent pipeline.

## Step 0: Setup

Run `which deepaper` to check. If not found: `pip install deepaper && deepaper init`.
If papers/ directory exists, skip init.

## Step 1: Download & Extract

```bash
deepaper download $ARGUMENTS
```
Parse JSON output → record ARXID, PDF_PATH.

```bash
deepaper extract ARXID
```
Parse JSON output → record RUN_DIR, TOTAL_PAGES, CORE_FIGURES, TABLE_DEF_PAGES.

## Step 2: Extractor Agent

```bash
deepaper prompt ARXID --role extractor
```
Parse JSON output → prompt_file. Read the prompt file content.
Spawn one Agent (subagent_type: executor, name: extractor) with that prompt content as the agent's task.
Wait for it to finish writing notes.md.

Verify notes exist:
```bash
wc -c .deepaper/runs/ARXID/notes.md
```
If <5,000 chars, notes are incomplete.

```bash
deepaper check ARXID
```
If passed=false → read the check.json failures. Spawn one retry Agent (subagent_type: executor, name: extractor-retry) with instructions to supplement notes.md based on the specific failures. Max 1 retry.

## Step 3: Writers (parallel)

```bash
deepaper prompt ARXID --split
```
Parse JSON output → writers array with prompt_file for each writer.

For EACH writer in the array, spawn an Agent (subagent_type: executor) in parallel:
- Read the writer's prompt_file content
- Give it as the agent's task prompt
- Name it the writer's name from the config

All writer prompts already contain: system role, quality contract, figure contexts (灵魂图广播), template instructions, format rules.

Wait for all writers to complete.

## Step 4: Merge + Gates

```bash
deepaper merge ARXID
deepaper gates ARXID
```

If gates passed=false:
```bash
deepaper fix ARXID
```
Read the prompt_file from fix output. Spawn a Fixer Agent (subagent_type: executor, name: fixer) with that prompt content. Fixer writes merged_fixed.md, then copy it as final.md.
Re-run `deepaper gates ARXID` on the fixed version (max 2 rounds total).

If gates passed=true: final.md is already set by merge.

## Step 5: Classify + Save

```bash
deepaper classify ARXID
```
Read the prompt_classify.md content. It contains the full category rules (4 categories, 13 subcategories, 3 classification principles). Based on the paper's content, determine the category yourself and output JSON: {"category": "llm/pretraining"}.

```bash
deepaper save ARXID --category CATEGORY --input .deepaper/runs/ARXID/final.md
```

Report the saved path and category to the user.
