# Diagram-to-Blog-Part Mapping

This document provides a clear mapping of which diagrams to use in which blog parts, including placement recommendations and context.

---

## Overview

**Total Diagrams:** 6 (4 Mermaid images, 1 ASCII, 1 Markdown table)
**Distribution:** Balanced across 5 blog parts (average 1-2 diagrams per part)

---

## Part 1: Introduction to Spec-Driven Development

**Target:** 1,200-1,500 words (5-6 min read)

### Primary Diagram

**Diagram:** SDD vs Traditional AI Chat Comparison
- **File:** `sdd-vs-traditional-comparison.png` (Mermaid) OR ASCII alternative
- **Placement:** After defining SDD, before OpenSpec comparison
- **Section:** "How SDD Differs from Ad-Hoc AI Chat"
- **Purpose:** Visually contrast trial-and-error loop vs structured path
- **Alt Text:** "Side-by-side comparison: Traditional AI Chat shows trial-and-error loop with vague prompts leading to repeated attempts until code works. Spec-Driven Development shows linear progression from requirements to specification to implementation to reviewable output."

**Contextual Flow:**
1. Introduce SDD concept in text (250-350 words)
2. Add introductory text: "The contrast is striking. Traditional AI chat often becomes a trial-and-error loop..."
3. Embed diagram (image or ASCII code block)
4. Follow with explanation of key benefits: predictability, reviewability, iterative refinement

### Optional Diagram

**Diagram:** OpenSpec vs Agent-OS Comparison Table
- **Format:** Markdown table (no image)
- **Placement:** In "Other SDD Approaches" subsection
- **Section:** Brief OpenSpec comparison (1-2 paragraphs)
- **Purpose:** Show different SDD methodologies, position agent-os
- **Context:** Keep minimal, not main focus of Part 1

**Note:** If Part 1 is approaching upper word limit, move this table to Part 5 conclusion instead.

---

## Part 2: The Station Station Project

**Target:** 1,400-1,700 words (6-7 min read)

### Primary Diagram

**Diagram:** Station Station Feature Implementation Timeline
- **File:** `station-station-timeline.png` (Mermaid Gantt) OR ASCII alternative
- **Placement:** After describing 8-feature roadmap, before technical challenges
- **Section:** "Development Timeline: 8 Features in 2-3 Days"
- **Purpose:** Prove SDD effectiveness with real, compressed timeline
- **Alt Text:** "Gantt chart showing Station Station development timeline from October 31 to November 2, 2025. Phase 1 Foundation includes authentication and API reverse engineering. Phase 2 Data Layer covers SDK, card selection, and attendance logic. Phase 3 Integration and UI includes GitHub integration, frontend dashboard, and configuration management."

**Contextual Flow:**
1. List all 8 completed roadmap features with phase groupings
2. Add introductory text: "Station Station was built incrementally over just 2-3 days using the agent-os SDD approach..."
3. Embed timeline diagram
4. Follow with explanation of phase dependencies: Phase 1 blocker (Cloudflare bypass), then rapid Phase 2-3 progression

**Recommendation:** Use Mermaid-rendered Gantt chart (more professional) rather than ASCII for this diagram, as timeline visualization benefits from graphical format.

---

## Part 3: Agent-OS Workflow in Action

**Target:** 1,500-1,800 words (7 min read)

### Primary Diagram 1

**Diagram:** Agent-OS Workflow Diagram
- **File:** `agent-os-workflow-diagram.png` (Mermaid)
- **Placement:** After explaining all 5 workflow phases, before highlighting review checkpoints
- **Section:** "The Complete Agent-OS Workflow"
- **Purpose:** Show iterative cycle with feedback loop
- **Alt Text:** "Agent-OS workflow diagram showing iterative cycle: Create Product, Shape Spec, Write Spec, Write Tasks, Implement Tasks, Human Review with feedback loop for debugging and refinement until feature is complete."

**Contextual Flow:**
1. Explain all 5 phases with Station Station examples (Create Product, Shape Spec, Write Specs, Write Tasks, Implement Tasks)
2. Add introductory text: "The agent-os workflow follows a structured, iterative cycle..."
3. Embed workflow diagram
4. Highlight the feedback loop: not linear, but iterative with human review

### Primary Diagram 2

**Diagram:** Agent-OS Task Execution Flow Sequence Diagram
- **File:** `agent-os-task-execution-flow.png` (Mermaid)
- **Placement:** After workflow diagram, in "Human Review at Key Decision Points" section
- **Section:** "When and How Humans Review AI Work"
- **Purpose:** Illustrate continuous human-AI collaboration, not just end review
- **Alt Text:** "Sequence diagram showing Agent-OS task execution flow: Human provides feature idea to Spec Writer, who gathers requirements and generates detailed spec. Task Writer breaks spec into tasks for Human approval. Task Implementer executes each task, writes tests, and submits for Review. Human reviews results and either approves or provides guidance for fixes. Process loops until feature is complete."

**Contextual Flow:**
1. Embed workflow diagram first (high-level overview)
2. Discuss human review checkpoints in text
3. Add introductory text: "This sequence diagram reveals the continuous human-AI collaboration throughout development..."
4. Embed sequence diagram (detailed interactions)
5. Emphasize: review happens at multiple stages, not just at end

**Note:** Part 3 has 2 diagrams, which is appropriate given it's the technical deep-dive part explaining the complete workflow.

---

## Part 4: Real Challenges and AI Limitations

**Target:** 1,600-1,800 words (7 min read)

### Primary Diagram

**Diagram:** When AI Needs Human Help - Collaboration Spectrum
- **Format:** ASCII diagram in code block
- **Placement:** After manualAttendanceDates debugging story, before explaining orchestrate tasks decision
- **Section:** "The AI-Human Collaboration Spectrum"
- **Purpose:** Set realistic expectations about AI capabilities and limitations
- **Alt Text:** "Three-tier collaboration spectrum diagram showing: Tier 1 - AI Can Handle Alone (boilerplate, CRUD, tests, simple components); Tier 2 - AI + Human Review Required (complex logic, APIs, refactoring, performance); Tier 3 - Human Must Lead (debugging, architecture, security, domain expertise). Includes real example of manualAttendanceDates bug where AI failed but human identified the problem location."

**Contextual Flow:**
1. Present manualAttendanceDates debugging story in detail (350-400 words with code snippet)
2. Share 2-3 additional challenge examples (timezone, Cloudflare bypass, API reverse engineering)
3. Add introductory text: "Not all coding tasks are equal when it comes to AI assistance..."
4. Embed ASCII collaboration spectrum diagram (in code block)
5. Position manualAttendanceDates as Tier 3 example (Human Must Lead)
6. Follow with guidance on setting up review checkpoints

**Note:** ASCII format works well here—it's more informal and honest, matching the authentic tone of this part about limitations.

---

## Part 5: Conclusion and Resources

**Target:** 1,500-1,700 words (6-7 min read)

### Optional Diagram

**Diagram:** OpenSpec vs Agent-OS Comparison Table
- **Format:** Markdown table (no image)
- **Placement:** In "Decision Framework: When to Use SDD" section or "Alternative Approaches" subsection
- **Section:** Comparing SDD methodologies (optional)
- **Purpose:** Help readers choose between SDD approaches based on use case
- **Alt Text:** "Comparison table of OpenSpec vs Agent-OS showing differences in focus, workflow, AI tool support, best use cases, spec format, orchestration capabilities, and setup complexity. Both are valid spec-driven development approaches for different use cases."

**Contextual Flow (if included):**
1. Provide decision framework for when to use agent-os SDD (greenfield projects, solo developers, etc.)
2. Contrast with when traditional AI chat suffices
3. Add introductory text: "Both OpenSpec and agent-os are valid SDD approaches solving different problems..."
4. Insert comparison table
5. Emphasize: choose based on your use case, not "better/worse"

**Note:** Only include this table if:
- Word count allows (Part 5 not exceeding 1,700 words)
- Flow supports it naturally
- It wasn't already used in Part 1

If table was used in Part 1, skip it here. If Part 5 is too long, skip this optional diagram.

---

## Diagram Distribution Summary

| Part | Primary Diagram(s) | Optional | Total | Rationale |
|------|-------------------|----------|-------|-----------|
| Part 1 | SDD vs Traditional (1) | OpenSpec table | 1-2 | Introduction needs clear SDD comparison |
| Part 2 | Timeline (1) | None | 1 | Project overview benefits from visual timeline |
| Part 3 | Workflow + Sequence (2) | None | 2 | Technical deep-dive justifies 2 diagrams |
| Part 4 | Collaboration Spectrum (1) | None | 1 | Limitations part needs realistic spectrum |
| Part 5 | None | OpenSpec table | 0-1 | Conclusion focuses on text, table optional |
| **Total** | **5** | **1** | **5-6** | Balanced distribution |

**Balance Check:**
- ✅ No part has more than 2 diagrams (avoids overwhelming readers)
- ✅ No part has zero visual elements except Part 5 (conclusion focused)
- ✅ Technical parts (Part 3) have more diagrams than narrative parts
- ✅ Distribution matches content density and complexity

---

## Medium Embedding Best Practices

### For Mermaid-Rendered Images (PNG):

1. **Upload to Medium:**
   - Drag and drop PNG file into Medium editor
   - Medium will auto-upload and embed

2. **Add Alt Text:**
   - Click on embedded image
   - Click "Alt text" button
   - Paste alt text from accessibility guide

3. **Add Caption (Optional):**
   - Click image
   - Add caption below image (e.g., "Agent-OS workflow showing iterative development cycle")

4. **Placement:**
   - Always add introductory text BEFORE image
   - Add 1-2 paragraphs explaining diagram AFTER image

### For ASCII Diagrams (Code Blocks):

1. **Insert Code Block:**
   - Type three backticks (```) in Medium editor
   - Select "Plain Text" or leave blank (no language identifier)

2. **Paste Diagram:**
   - Copy ASCII diagram exactly (preserve spacing and alignment)
   - Test in preview mode to ensure monospace rendering

3. **Placement:**
   - Add introductory text BEFORE code block
   - Add explanation AFTER code block

### For Markdown Tables:

1. **Insert Directly:**
   - Paste markdown table syntax into Medium editor
   - Medium will auto-format as table

2. **Format Check:**
   - Preview to ensure table renders correctly
   - Verify column alignment

3. **Placement:**
   - Add context paragraph BEFORE table
   - Add takeaway or conclusion AFTER table

---

## Diagram Quality Checklist

Before embedding diagrams in Medium:

- [ ] All Mermaid diagrams rendered to PNG and saved in `/visuals/` folder
- [ ] All PNG files under 1MB (preferably under 500KB)
- [ ] Station Station timeline uses actual dates (Oct 31 - Nov 2, 2025)
- [ ] All diagrams have alt text prepared
- [ ] All diagrams have introductory text written
- [ ] ASCII diagrams tested in monospace code blocks
- [ ] Diagram placement mapped to specific blog sections
- [ ] Distribution is balanced (1-2 diagrams per part)
- [ ] All diagrams support blog narrative (not decorative)

---

## Recommended Diagram Order for User

**Rendering Priority (most important first):**

1. **Station Station Timeline** (Part 2) - Core proof of SDD effectiveness
2. **SDD vs Traditional Comparison** (Part 1) - Foundational concept illustration
3. **Agent-OS Workflow** (Part 3) - Central to workflow explanation
4. **Task Execution Flow** (Part 3) - Detailed workflow sequence
5. **Collaboration Spectrum** (Part 4) - Use ASCII, no rendering needed
6. **OpenSpec Table** (Part 1 or 5) - Use markdown, no rendering needed

**If time is limited:** Render diagrams 1-4, use ASCII/markdown alternatives for 5-6.

---

**Document Version:** 1.0
**Purpose:** Guide diagram usage across all 5 blog parts
**Status:** Ready for content creation (Task Groups 3-7)
