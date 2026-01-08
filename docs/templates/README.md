Templates Index — APIS-OVERSEER

Purpose:
This folder contains all standardized, low-friction templates used to coordinate work across humans and AI agents in APIS-OVERSEER.

These templates exist to:

Reduce cognitive load

Prevent process drift

Preserve reconstruction under interruption

Keep governance lighter than the work itself

If a document exists in this folder, it has passed the fatigue-resistance test.

🧭 How to Use This Folder

You do NOT need all templates for every task

Choose the lightest template that fits the situation

Templates are tools, not rituals

If you feel friction, you are probably using a heavier template than needed.

📦 Template Inventory (Current)
1. LOOP_MODE_TEMPLATE.md

What it is:
Declares how work is allowed to move before it starts.

Use when:

More than 2 agents involved

Work spans sessions or days

Architectural / performance constraints matter

You want a clean archive trail

Do NOT use for:

Casual brainstorming

One-off ideas

Solo experimentation

Think of this as the router, not the payload.

2. MEMO_TEMPLATE.md

What it is:
Primary communication unit between agents.

Use when:

Sending structured information

Making decisions or recommendations

Handing work between roles

Key constraints:

WHY field capped at 140 characters

Tables over prose

Designed for 15s reconstruction

This is the default template.

3. HANDOFF_TEMPLATE.md

What it is:
Formal transfer of responsibility between agents.

Use when:

Moving between loop steps

Passing work to an implementer

Transitioning ownership

Keeps momentum without ambiguity.

4. CONSENSUS_DIGEST_TEMPLATE.md

What it is:
Compresses multi-agent agreement into a single artifact.

Use when:

Multiple perspectives must converge

A decision needs durable clarity

Avoiding “we agreed, but…” situations

Often precedes loop termination.

5. ARBITRATION_MEMO_TEMPLATE.md

What it is:
Conflict resolution and tie-break mechanism.

Use when:

Agents disagree materially

Tradeoffs cannot be reconciled organically

A decision must be forced cleanly

Rare by design. High signal when used.

6. GOVERNANCE_QUICK_REFERENCE.md

What it is:
Human-readable memory scaffold.

Use when:

Re-orienting after time away

Onboarding a returning agent

Checking invariants without rereading full governance docs

This is the wake-up card for the system.

🧠 Template Selection Heuristic

Ask yourself:

“What is the lightest artifact that will keep this work from drifting?”

Idea bouncing → No template

Small change → MEMO or PML + HANDOFF

Feature work → LOOP_MODE + MEMO

Disagreement → CONSENSUS or ARBITRATION

Confusion → GOVERNANCE_QUICK_REFERENCE

🔒 Governance Notes

Templates may evolve, but never proliferate

Adding a new template requires justification

Removing one is always allowed

If templates become heavier than the work, the system has failed.