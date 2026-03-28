---
name: notebooklm
description: Use when the user is working with Google NotebookLM at any stage — preparing sources, querying notebooks, processing Audio Overviews or study guides, or managing multiple notebooks
---

# NotebookLM Workflow Assistant

## Overview
4-stage workflow: **Prepare** → **Organize** → **Query** → **Process**. Claude assists at every stage but cannot automate NotebookLM directly (no public API).

## Stage 1 — Prepare Sources

**When:** Before uploading to NotebookLM.

**What Claude does:**
- Summarizes long PDFs and cleans web articles into structured markdown
- Extracts key points from YouTube transcripts
- Splits large documents into focused topic chunks

| Source | Ask Claude |
|--------|-----------|
| PDF | "Summarize this PDF into key points ready for NotebookLM upload" |
| Web URL | "Clean and structure this article for NotebookLM upload" |
| YouTube transcript | "Extract key points from this transcript for NotebookLM" |
| Google Doc/Slides | "Condense this into a focused summary for NotebookLM" |

## Stage 2 — Upload & Organize

**When:** Setting up a new notebook or managing multiple notebooks.

**What Claude does:** Suggests notebook names and groupings, reviews source lists for overlap or gaps, recommends how to split large projects across notebooks.

**Example:** "Here are my 8 sources on [topic] — how should I organize them into notebooks?"

## Stage 3 — Query Strategy

**When:** Asking questions inside NotebookLM.

**What Claude does:** Suggests questions for your goal (research, study, content creation), writes prompts to trigger specific outputs, generates follow-ups to go deeper.

| Output type | Prompt to use in NotebookLM |
|-------------|----------------------------|
| FAQ | "Create a FAQ based on the key questions in these sources" |
| Study guide | "Create a study guide with definitions and key concepts" |
| Briefing doc | "Summarize the key facts and arguments across all sources" |
| Audio Overview | "Create a podcast-style conversation covering the main ideas" |

**Follow-ups inside NotebookLM:** "Which source supports this? Expand on [point]. What are the counterarguments?"

## Stage 4 — Process Outputs

**When:** You have output from NotebookLM and need it in a usable format.

**What Claude does:** Reformats Audio Overview transcripts into structured notes, synthesizes multiple outputs into one document, converts FAQ/study guide output into flashcards or drafts.

**Example prompts:**
- "Reformat this Audio Overview transcript into bullet-point notes"
- "Combine these NotebookLM summaries into one briefing document"
- "Turn this FAQ into flashcards"

## Quick Reference

| Task | Ask Claude |
|------|-----------|
| Prepare a PDF | "Summarize this PDF into key points for NotebookLM" |
| Prepare a YouTube transcript | "Extract key points from this YouTube transcript for NotebookLM" |
| Plan notebook structure | "Help me organize these [N] sources into notebooks on [topic]" |
| Generate questions to ask | "What should I ask NotebookLM about [topic]?" |
| Clean up Audio Overview | "Reformat this Audio Overview transcript into structured notes" |
| Synthesize multiple outputs | "Combine these NotebookLM outputs into one document" |
