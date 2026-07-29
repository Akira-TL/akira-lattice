# general-word-document-generation

## What it does

This skill generates and revises DOCX files through Word-native document semantics. It builds pages, sections, styles, paragraphs, tables, captions, fields, pagination, and character formatting instead of transferring Markdown or web UI conventions into Word.

Its default output is formal, restrained, printable, and visually stable. Text, headings, table styling, borders, headers, footers, and decorative elements remain black and white unless the user explicitly requests another visual system. Photographs, scientific figures, screenshots, maps, diagrams, and data visualizations may retain original or informative color.

## When to use it

Use this skill when creating, rewriting, formatting, or quality-checking a general Word document, especially when the result must be ready to submit without manually fixing colored headings, decorative tables, Markdown blockquotes, bullet-heavy prose, unstable pagination, or inconsistent typography.

It adapts to academic papers, research reports, project proposals, business reports, notices, formal statements, operating manuals, and technical documentation. Explicit user, institutional, journal, or project formatting requirements override its defaults.

## Key behavior

The skill starts from a blank DOCX unless the user explicitly requires a supplied template. It defines a coherent Word style system, converts content into semantic document objects, applies character-level scientific formatting where needed, and renders the result page by page for visual inspection before delivery.

Chinese text uses full-width Chinese punctuation and “double” or ‘nested’ quotation marks. Latin genus and species names use real italic formatting. Statistical symbols such as *P* use semantic italic formatting rather than visible Markdown markers.

## Source

Runtime instructions are maintained at:

```text
skills/productivity/general-word-document-generation/SKILL.md
```

Installation and update commands will be documented after the repository's distribution method is chosen.
