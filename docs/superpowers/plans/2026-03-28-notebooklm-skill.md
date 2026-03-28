# NotebookLM Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a `notebooklm` Claude skill that guides users through the full NotebookLM workflow — prepare sources, organize notebooks, query effectively, and process outputs.

**Architecture:** Single `SKILL.md` file at `~/.claude/skills/notebooklm/SKILL.md`. Follows Workflow Overview + Task Cards structure. TDD for skills: RED baseline → GREEN write skill → REFACTOR close loopholes.

**Tech Stack:** Markdown, YAML frontmatter, Claude Code skills system (`~/.claude/skills/`)

---

## Task 1: RED — Establish Baseline Behavior

**Files:**
- Read: `~/.claude/skills/` (confirm notebooklm skill does NOT exist yet)

- [ ] **Step 1: Confirm skill does not exist**

Run:
```bash
ls ~/.claude/skills/
```
Expected: No `notebooklm` directory listed.

- [ ] **Step 2: Document expected baseline failures**

Without the skill, an agent asked "Help me use NotebookLM" will likely:
- Give generic advice not specific to NotebookLM's actual features
- Miss the 4-stage workflow structure
- Not offer per-source-type preparation guidance
- Not provide NotebookLM-specific prompt templates for FAQs, Audio Overviews, etc.
- Not help with notebook organization strategy

Record these as the gaps the skill must close.

- [ ] **Step 3: Commit baseline documentation**

```bash
git add docs/superpowers/plans/2026-03-28-notebooklm-skill.md
git commit -m "plan: notebooklm skill baseline and implementation plan"
```

---

## Task 2: GREEN — Write the Skill

**Files:**
- Create: `~/.claude/skills/notebooklm/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p ~/.claude/skills/notebooklm
```

- [ ] **Step 2: Write SKILL.md**

Create `~/.claude/skills/notebooklm/SKILL.md` with this exact content:

```markdown
---
name: notebooklm
description: Use when the user is working with Google NotebookLM at any stage — preparing sources, querying notebooks, processing Audio Overviews or study guides, or managing multiple notebooks
---

# NotebookLM Workflow Assistant

## Overview
Google NotebookLM lets you upload sources and ask questions across them. Your workflow has 4 stages: **Prepare** → **Organize** → **Query** → **Process**. Claude assists at every stage — but cannot automate NotebookLM directly (no public API).

## Stage 1 — Prepare Sources

**When:** Before uploading to NotebookLM.

**What Claude does:**
- Summarizes long PDFs into key points
- Cleans messy web articles into structured markdown
- Extracts key points from YouTube transcripts
- Splits large documents into focused topic chunks

| Source | Ask Claude |
|--------|-----------|
| PDF | "Summarize this PDF into key points ready for NotebookLM upload" |
| Web URL | "Clean and structure this article for NotebookLM upload" |
| YouTube transcript | "Extract key points from this transcript for NotebookLM" |
| Google Doc / Slides | "Condense this into a focused summary for NotebookLM" |

## Stage 2 — Upload & Organize

**When:** Setting up a new notebook or managing multiple notebooks.

**What Claude does:**
- Suggests notebook names and topic groupings
- Reviews your source list for overlap or gaps
- Recommends how to split large projects across notebooks

**Example prompt:** "Here are my 8 sources on [topic] — how should I organize them into notebooks?"

## Stage 3 — Query Strategy

**When:** Ready to ask questions inside NotebookLM.

**What Claude does:**
- Suggests questions based on your goal (research, study, content creation)
- Writes prompts to trigger specific NotebookLM outputs
- Generates follow-up prompts to go deeper

| Output type | Prompt to use in NotebookLM |
|-------------|----------------------------|
| FAQ | "Create a FAQ based on the key questions in these sources" |
| Study guide | "Create a study guide with definitions and key concepts" |
| Briefing doc | "Summarize the key facts and arguments across all sources" |
| Audio Overview | "Create a podcast-style conversation covering the main ideas" |

**Follow-up pattern inside NotebookLM:** "Which source supports this? Can you expand on [point]? What are the counterarguments?"

## Stage 4 — Process Outputs

**When:** You have output from NotebookLM and need it in a usable format.

**What Claude does:**
- Reformats Audio Overview transcripts into structured notes
- Synthesizes multiple NotebookLM outputs into one document
- Converts FAQ / study guide output into outlines, flashcards, or drafts

**Example prompts to Claude:**
- "Reformat this Audio Overview transcript into bullet-point notes"
- "Combine these three NotebookLM summaries into one briefing document"
- "Turn this FAQ into a set of flashcards"

## Quick Reference

| Task | Ask Claude |
|------|-----------|
| Prepare a PDF | "Summarize this PDF into key points for NotebookLM" |
| Prepare a YouTube transcript | "Extract key points from this YouTube transcript for NotebookLM" |
| Plan notebook structure | "Help me organize these [N] sources into notebooks on [topic]" |
| Generate questions to ask | "What should I ask NotebookLM about [topic]?" |
| Clean up Audio Overview | "Reformat this Audio Overview transcript into structured notes" |
| Synthesize multiple outputs | "Combine these NotebookLM outputs into one document" |
```

- [ ] **Step 3: Verify file was written**

```bash
cat ~/.claude/skills/notebooklm/SKILL.md
```
Expected: Full skill content visible, frontmatter at top, 4 stage cards present.

- [ ] **Step 4: Commit the skill**

```bash
git add ~/.claude/skills/notebooklm/SKILL.md
git commit -m "feat: add notebooklm workflow assistant skill"
```

---

## Task 3: REFACTOR — Verify and Close Loopholes

**Files:**
- Read: `~/.claude/skills/notebooklm/SKILL.md`
- Edit: `~/.claude/skills/notebooklm/SKILL.md` (if loopholes found)

- [ ] **Step 1: Check token count**

```bash
wc -w ~/.claude/skills/notebooklm/SKILL.md
```
Expected: Under 500 words. If over, trim Quick Reference or condense Stage card prose.

- [ ] **Step 2: Verify frontmatter character count**

```bash
head -5 ~/.claude/skills/notebooklm/SKILL.md | wc -c
```
Expected: Under 1024 characters total for the frontmatter block.

- [ ] **Step 3: Check skill is discoverable**

```bash
ls ~/.claude/skills/notebooklm/
```
Expected: `SKILL.md` listed.

- [ ] **Step 4: Verify all 4 stages are present**

```bash
grep "## Stage" ~/.claude/skills/notebooklm/SKILL.md
```
Expected: 4 lines — Stage 1, 2, 3, 4.

- [ ] **Step 5: Verify Quick Reference table has 6 rows**

```bash
grep -c "| " ~/.claude/skills/notebooklm/SKILL.md
```
Expected: At least 20 table rows across all tables (headers + data rows).

- [ ] **Step 6: Commit if changes were made**

```bash
git add ~/.claude/skills/notebooklm/SKILL.md
git commit -m "refactor: tighten notebooklm skill after verification"
```
(Skip if no changes needed.)

---

## Checklist Summary

- [ ] Task 1: Baseline documented, plan committed
- [ ] Task 2: SKILL.md written and committed
- [ ] Task 3: Verified discoverable, under token limit, all stages present
