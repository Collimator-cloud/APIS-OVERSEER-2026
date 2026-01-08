# GOVERNANCE QUICK REFERENCE CARD

**For:** All Claude Code agents
**Purpose:** Fast reference for Phase 5 Archive Governance compliance

---

## 📋 TASK COMPLETION CHECKLIST

Before completing any task:

- [ ] Update [PROJECT_STATE.md](../../PROJECT_STATE.md) Line 1 with current WAKE-UP line
- [ ] Add Chronicle entry to [PROJECT_STATE.md](../../PROJECT_STATE.md) (verify WHY ≤140 chars)
- [ ] Validate all memo filenames match `YYYY-MM-DD_[TAG]_[NAME].md`
- [ ] Confirm Lock Check = YES

---

## 🎯 WAKE-UP LINE FORMAT

**Location:** [PROJECT_STATE.md:1](../../PROJECT_STATE.md#L1)

**Format:**
```markdown
> **WAKE-UP:** [PHASE_NAME] | [YYYY-MM-DD] | [MEMO_ID] | RECONSTRUCTION: <15s
```

**Example:**
```markdown
> **WAKE-UP:** PHASE_5_ARCHIVE_GOVERNANCE | 2026-01-07 | 2026-01-07-Phase5-Archive | RECONSTRUCTION: <15s
```

**Rules:**
- Must be Line 1 of PROJECT_STATE.md
- Four pipe-separated fields required
- `RECONSTRUCTION: <15s` is literal (not calculated)
- Update at every task completion

---

## 📝 MEMO FILENAME CONVENTION

**Format:** `YYYY-MM-DD_[TAG]_[SHORT_NAME].md`

**Examples:**
- `2026-01-07_GOV_Phase5_Archive_Governance.md` ✅
- `2026-01-08_PERF_Numba_Optimization.md` ✅
- `2026-01-09_BIOL_Foraging_Behavior.md` ✅

**Invalid:**
- `phase5_governance.md` ❌ (missing date and tag)
- `2026-01-07-governance.md` ❌ (wrong separator, missing tag)
- `01-07-2026_GOV_Archive.md` ❌ (wrong date format)

---

## 🏷️ TAG DEFINITIONS

| Tag | Purpose | Storage Location |
| :--- | :--- | :--- |
| `PERF` | Performance optimization, benchmarks | `docs/memos/specs/` |
| `BIOL` | Biological metaphors, agent lifecycle | `docs/memos/specs/` |
| `ARCH` | Architecture decisions, system design | `docs/memos/specs/` |
| `GOV` | Governance, process, protocol | `docs/memos/governance/` |
| `IMPL` | Implementation details, features | `docs/memos/specs/` |
| `PERC` | Perception layer, UI/UX, visual | `docs/memos/specs/` |

---

## ✂️ WHY FIELD: 140-CHARACTER HARD CAP

**Rule:** WHY field must be ≤140 characters (including spaces and punctuation)

**Validation:**
```python
len(why_text) <= 140  # Must be True
```

**Examples:**

✅ **PASS (47 chars):**
```
"Implementation of Phase 5 Archive governance."
```

✅ **PASS (139 chars):**
```
"Establish archive governance to ensure memo consistency, enforce WHY cap, and maintain reconstruction speed compliance."
```

❌ **FAIL (157 chars):**
```
"This is an extremely long WHY field that exceeds the 140-character limit and will be rejected by the validation system because it is too verbose and not concise."
```

**Action on Violation:**
- Reject memo save
- Display character count
- Prompt for truncation

---

## 📜 CHRONICLE ENTRY FORMAT

**Location:** [PROJECT_STATE.md](../../PROJECT_STATE.md) → `## 📜 RECENT EVOLUTIONS`

**Table Format:**
```markdown
| ID | Date | Role | Tag | Why (Max 140) | Lock Check |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 001 | 2026-01-07 | ARCH | GOV | Implementation of Phase 5 Archive governance. | YES |
```

**Rules:**
- ID: 3-digit zero-padded (001, 002, 003...)
- Date: ISO format (YYYY-MM-DD)
- Role: ARCH, BUILDER, PERF, BIOLOGIST, etc.
- Tag: One of 6 tags (PERF, BIOL, ARCH, GOV, IMPL, PERC)
- WHY: ≤140 characters
- Lock Check: YES or NO

---

## 📁 DIRECTORY STRUCTURE

```
docs/
├── memos/
│   ├── triage/         # Error logs, debugging chronicles
│   ├── specs/          # Feature designs, implementation plans
│   └── governance/     # Process definitions, protocols
├── baselines/          # Version snapshots
│   └── [version]/
│       ├── MANIFEST.md
│       └── visual_baseline.png (≤150KB)
└── templates/          # Standardized templates
    ├── MEMO_TEMPLATE.md
    ├── MANIFEST_TEMPLATE.md
    ├── HANDOFF_TEMPLATE.md
    └── ...
```

---

## 🎬 HANDOFF PROTOCOL

### Pre-Handoff Checklist

1. ✅ Update PROJECT_STATE.md WAKE-UP line
2. ✅ Add Chronicle entry with Lock Check = YES
3. ✅ Verify WHY field ≤140 characters
4. ✅ Confirm memo filenames match convention
5. ✅ Save in-progress work with clear TODO markers

### Handoff Message Template

```markdown
> **WAKE-UP:** [PHASE_NAME] | [DATE] | [LATEST_MEMO_ID] | RECONSTRUCTION: <15s

**Status:** [Task completion summary]

**Lock Check:** YES — All context preserved.

**Next Steps:**
1. [Action item 1]
2. [Action item 2]

**Reference Memos:**
- [Memo 1](docs/memos/.../file.md)
- [Memo 2](docs/memos/.../file.md)
```

---

## ⚡ COMMON VIOLATIONS & FIXES

### ❌ WHY field exceeds 140 characters

**Fix:** Truncate or rephrase to be more concise

**Before (157 chars):**
```
"This implementation adds a new feature to the system that allows users to track their usage metrics and export them to various file formats for analysis."
```

**After (139 chars):**
```
"Add usage metrics tracking with export to multiple formats (CSV, JSON, XML) for analysis and reporting."
```

---

### ❌ Wrong filename format

**Wrong:** `governance_memo.md`
**Right:** `2026-01-07_GOV_Phase5_Archive_Governance.md`

---

### ❌ WAKE-UP line missing or malformed

**Wrong:**
```markdown
# PROJECT STATE
```

**Right:**
```markdown
> **WAKE-UP:** PHASE_5_ARCHIVE_GOVERNANCE | 2026-01-07 | 2026-01-07-Phase5-Archive | RECONSTRUCTION: <15s

# PROJECT STATE
```

---

### ❌ Chronicle entry missing Lock Check

**Wrong:**
```markdown
| 001 | 2026-01-07 | ARCH | GOV | Phase 5 governance. | |
```

**Right:**
```markdown
| 001 | 2026-01-07 | ARCH | GOV | Phase 5 governance. | YES |
```

---

## 🔍 VALIDATION COMMANDS

### Check WAKE-UP line
```bash
head -n 1 PROJECT_STATE.md
```

### Count Chronicle entries
```bash
grep "^|" PROJECT_STATE.md | tail -n +2 | wc -l
```

### List memos by tag
```bash
ls docs/memos/specs/*_PERF_*.md
ls docs/memos/governance/*_GOV_*.md
```

### Validate WHY field length (manual)
```python
why = "Your WHY field text here"
print(f"Length: {len(why)} chars - {'PASS' if len(why) <= 140 else 'FAIL'}")
```

---

## 📚 FULL DOCUMENTATION

For complete governance rules, see:
- [docs/memos/governance/2026-01-07_GOV_Phase5_Archive_Governance.md](../memos/governance/2026-01-07_GOV_Phase5_Archive_Governance.md)

For templates:
- [MEMO_TEMPLATE.md](MEMO_TEMPLATE.md)
- [MANIFEST_TEMPLATE.md](../baselines/MANIFEST_TEMPLATE.md)
- [HANDOFF_TEMPLATE.md](HANDOFF_TEMPLATE.md)

---

**Quick Start:** Read [PROJECT_STATE.md](../../PROJECT_STATE.md) WAKE-UP line → Chronicle → Referenced memos = <15s context reconstruction ✅

**Lock Check:** YES — Quick reference validated and ready for agent use.
