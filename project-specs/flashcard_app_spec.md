# Flashcard App Prototype – Functional Specification&#x20;

**Goal**  Build a minimal CLI prototype that ingests a Readlang export (`.tsv`), enriches it with AI‑generated examples, and serves spaced‑repetition flashcards in two practice modes (Multiple‑Choice “Blitz” and Typing “Mastery”).

---

## 1 Scope Overview

### Included in this first prototype

- **Import** – one Tab‑separated file with two columns:  `translation <TAB> context_sentence_with_[[target]]`  (e.g., `assumido<TAB>Peter has [[taken up]] his English…`).
- **Targets / Examples / Cards** flat data model saved in a single `data.json` file and held in memory at runtime.
- **AI examples** – keep the original example **plus N** LLM‑generated **contextual** examples (same sense, new context).
- **Translation refinement** – LLM cleans each original Readlang pair before storage.
- **Spaced‑Repetition** – SM‑2 algorithm; per‑card statistics (`last_seen`, `next_due`, `interval`, `easiness`, `successes_in_row`).
- **Practice Modes / Card Ladder** – Meaning MCQ → Word MCQ → Typing, unlocked in order per example.
- **Hint system** – 3‑step hints for MCQs (alt sentence/synonyms/translation) and alternating prefix/suffix hints for Typing; each hint lowers the score.
- **Session structure** – each review session loads **4 examples → up to 16 cards**; wrong or “almost” answers reappear **two cards later**; queue avoids back‑to‑back cards from the same example.
- **CLI UI** – single‑user, text‑based interface with main menu (import, practice, help).

---

## 2 Input Specification (`.tsv`)

```tsv
translation<TAB>context_sentence
assumido<TAB>Peter has [[taken up]] his English with great reluctance.
embora<TAB>… automation, [[though]] often told as a story of the future…
```

**Parser**

1. Split each line on `\t`.
2. Column 0 → `translation` (base language).
3. Column 1 → `context`.
4. Extract the **target** from inside `[[…]]`.

---

## 3 Data Model (Entity → fields)

| Entity              | Fields                                                                                                                                                                                                                      |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Target**          | `id`, `target`, `lang`, `date_added`, `learned` (bool), `date_learned`                                                                                                                                                      |
| **Example**         | `id`, `target_id`, `text`, `example_target`, `example_type` (`contextual` only), `source` (readlang/ai/human), `parent_example_id` (nullable), `context_hint`, `contextual_synonyms`, `translations` (dict), `date_created` |
| **Card**            | `id`, `example_id`, `card_type` (MeaningMCQ/WordMCQ/Typing), `hints` (array of up to 3 strings), `review_stats`                                                                                                             |
| **ReviewStats**\*\* | `last_seen`, `next_due`, `interval` (days), `easiness` (float), `successes_in_row`, `mastered` (bool)                                                                                                                       |

All three entities live in **one** JSON document:

```json
{
  "targets":   [ … ],
  "examples":  [ … ],
  "cards":     [ … ]
}
```

---

## 4 Translation Refinement (LLM Pre‑processing)

Before any AI‑generated examples are created, each **original** Readlang row is cleaned up by an LLM so that the very first Example object we store is already **complete and schema‑compliant**.

**Workflow**

1. Import TSV line → extract `context_sentence`, `raw_translation` (column 0), and `target`.
2. Send the pair to a small LLM with this prompt:
   > *System*: You are a bilingual proof‑reader. Given an English sentence and its Portuguese translation (from Readlang), output a **single JSON object that conforms to the project’s ****\`\`**** schema**. Use the field names exactly as below. Set `example_type` to `"original"`, `source` to `"readlang"`, and leave `id`, `target_id`, and `parent_example_id` as `null` (they will be filled by the importer). The `translations.pt‑BR` entry must contain the corrected, natural Brazilian‑Portuguese sentence. If the supplied translation is acceptable, reuse it; otherwise return the improved version and optionally add a brief note in `notes`.
   >
   > ```json
   > {
   >   "id": null,
   >   "target_id": null,
   >   "example_type": "original",
   >   "source": "readlang",
   >   "parent_example_id": null,
   >   "example_target": "taken up",
   >   "text": "Peter has [[taken up]] his English with great reluctance.",
   >   "context_hint": null,
   >   "contextual_synonyms": [],
   >   "translations": { "pt-BR": ["assumido"] },
   >   "notes": "ok"
   > }
   > ```
3. The importer assigns real `id` and `target_id`, stores the object in the `examples` array, and (optionally) keeps a copy of the raw translation in `raw_translation` for audit purposes.
4. Only after this cleaned **original** Example is persisted do we proceed to generate the additional synthetic examples described in Section 5.

**Data‑model note** – add optional fields `notes` and `raw_translation` to the Example schema if audit trails are desired.



## 5 CLI Menu

When the user runs `flashcards` with no sub‑command, a simple text menu appears:

```
Flashcard CLI  –  What would you like to do?

 1) Start a practice session      (review due cards)
 2) Import a Readlang file (TSV)  (add new targets/examples)
 3) More info / help              (commands, shortcuts, data location)
 0) Exit

> _
```

### 5.1 Menu behaviour

| Key | Action                     | Equivalent CLI command                 | Notes                                                                                                                                        |
| --- | -------------------------- | -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `1` | **Start practice session** | `flashcards review`                    | Launches the spaced‑repetition loop described in Section 7.                                                                                  |
| `2` | **Import TSV**             | `flashcards import <path/to/file.tsv>` | Prompts for a file path if none supplied; runs the translation‑refinement pipeline (Section 4) and synthetic‑example generation (Section 6). |
| `3` | **More info / help**       | `flashcards help`                      | Displays a one‑page cheat‑sheet of keyboard shortcuts, data‑file locations, and a brief FAQ.                                                 |
| `0` | **Exit**                   | --                                     | Graceful termination.                                                                                                                        |

### 5.2 Navigation shortcuts

- Press `Esc` at any prompt to return to the main menu.
- While reviewing, press `?` to view the same help page without leaving the session.

---

## 6 Synthetic Example Generation

For the  prototype the system generates **contextual examples only**. Each target receives up to N  fresh sentences that preserve the original meaning but place the word in new contexts. This prevents memorising a single sentence and reinforces sense inference.

### 6.1 Generation workflow

1. Take the cleaned *original* Example (Section 4).
2. Prompt an LLM: *“Create up to 3 different English sentences that use \*\* with the ****same meaning**** as in the original. Wrap the word (or exact inflected form) in double brackets.”*
3. For each returned sentence, build an Example object with `example_type: "contextual"`, `parent_example_id` pointing to the original, and `source: "ai"`.
4. Store the objects in the `examples` array and immediately create the three Cards per Example.

### 6.2 Parent linking

If `example_type = "contextual"` set `parent_example_id` to the `id` of the original Example so lineage is preserved.

### 6.3 Mastery interaction

Contextual examples generate cards just like the original; their progress counts toward the target’s overall `learned` status.

---

## 7 Cards

### 7.1 Card Types & Prerequisite Chain

| `card_type`    | UI label      | Prompt style                                                                                                                                                     | Unlock condition                                                                                  |
| -------------- | ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **MeaningMCQ** | Meaning Match | Show full context with **target** in bold; learner picks the correct definition (4 options).                                                                     | First card shown for every example.                                                               |
| **WordMCQ**    | Word Choice   | Show context with the target blanked out; show the target’s definition; learner chooses the correct word from 4 options (1 answer + 3 AI‑generated distractors). | Becomes eligible after the learner answers the associated MeaningMCQ **correctly at least once**. |
| **Typing**     | Word Recall   | Same blanked‑context setup, but learner **types** the word. Definition may be paraphrased; optionally list common but wrong synonyms as guidance.                | Becomes eligible after the learner answers the WordMCQ **correctly at least once**.               |

### 7.2 Card Generation & Distractor Logic

At import time the system creates **three Card objects per Example** (`MeaningMCQ`, `WordMCQ`, `Typing`). Only the *unlocked* card joins the review queue; its siblings remain dormant until prerequisites are met.

#### MeaningMCQ

- **Hint system** (optional, sequential):

  1. *Hint 1* – an **alternative English sentence** that uses the target with the **same meaning**.
  2. *Hint 2* – a short list (≤ 3) of **English synonyms** for that sense.
  3. *Hint 3* – the **Brazilian‑Portuguese translation** of the target word. Learners reveal hints in order by pressing a “hint” key; each hint is appended to an onscreen stack so earlier hints remain visible. These three strings are pre‑generated during card creation and stored in the Card’s `hints` array `[alt_sentence, synonyms, pt_translation]` (unused slots may be `null`).

- **Distractors**: LLM produces **3 distractor definitions** (max 1 genuine dictionary sense + 2 plausible but wrong meanings). All four definitions are shuffled before display.

- **Scoring**: Using a hint does **not** mark the answer wrong, but reduces the SM‑2 quality score by 1 per hint revealed (minimum 2).

#### WordMCQ

- **Hint system** (optional, sequential):

  1. *Hint 1* – the **most obvious English synonym** for the blanked word.
  2. *Hint 2* – a **second, less obvious synonym** (still correct for the given sense).
  3. *Hint 3* – the **Brazilian‑Portuguese translation** of the target word. Store these in the Card’s `hints` array `[synonym1, synonym2, pt_translation]`.

- **Distractor generation**:

  - LLM proposes **9 distractor word forms** (details TBD). Saved in `distractor_forms`.
  - At each review, randomly sample **3** distractors, add the target, then **shuffle** the 4 options.

- **Scoring**: Each revealed hint lowers the SM‑2 quality score by 1 (minimum 2), mirroring MeaningMCQ.

#### Typing

- **Hint system** (optional, sequential & alternating):

  1. *Hint 1* – reveal a **prefix** of the target followed by an ellipsis (e.g., `"bri…"`).
  2. *Hint 2* – reveal a **suffix** of the target preceded by an ellipsis (e.g., `"…ming"`). The learner can request hints repeatedly; the card alternates between prefix and suffix on subsequent requests (Hint 3 would be the prefix again, Hint 4 the suffix, etc.). These two strings are stored in the Card’s `hints` array `[prefix_hint, suffix_hint]` and the UI cycles through them.

- **Answer evaluation**

  - Normalise both input and target (lower‑case, trim whitespace, unify apostrophes/diacritics).
  - Exact match → **correct**.
  - If **Levenshtein distance ≤ 1** *or* it differs only by a simple suffix/prefix slip → **typing mistake** ("almost").
  - Otherwise → **wrong**.

- **Scoring**: Each hint revealed lowers the SM‑2 quality score by 1, same as the other card types.

#### General notes

- Distractor generation happens **once** per Example during import; sampling & shuffling occur at runtime for freshness.
- The scheduler enforces the prerequisite ladder: a card is locked until its predecessor has at least **one correct** review.

### 7.3 Review Session Flow (CLI)

1. Each **practice session** loads **4 examples → 16 potential cards** (max). Examples are selected by lowest `next_due`, but the scheduler ensures that successive cards come from **different examples** whenever possible.
2. Only cards whose prerequisites are unlocked are queued (MeaningMCQ before WordMCQ, WordMCQ before Typing).
3. Queue order rule: never schedule two cards from the same Example back‑to‑back unless no other due cards exist.
4. Learner answers a card → grade, update `review_stats` via SM‑2.
5. **If the answer is wrong or "almost":**
   - Requeue the card **two positions later** (not at the very end) so the learner tries again after seeing at least two different cards.
   - Locked follower cards for that Example remain locked until the parent is answered correctly on a later appearance.
6. When the session completes (all due cards answered), recalculate each Target’s `learned` flag: a target is *learned* when **all three** cards are `mastered=true`.

### 7.4 Session Parameters

| Parameter         | Default | Rationale                                             |
| ----------------- | ------- | ----------------------------------------------------- |
| Examples per run  | 4       | Keeps a session lightweight (\~5–8 min).              |
| Cards per example | Up to 4 | Enforces full ladder; fewer if some are still locked. |
| Wrong‑answer bump | +2 pos  | Quick retry without immediate repetition.             |

---

## 8 CLI Cards Interface

Below are clean ASCII mock‑ups showing **one** card per type and how hints appear. Duplicate or stray boxes from earlier drafts have been removed.

### 8.1 MeaningMCQ

```text
┌──────────────────────────────────────────────────────────────┐
│  If you only knew how they **mock** me.                      │
├──────────────────────────────────────────────────────────────┤
│  What does “mock” mean here?                                 │
│                                                              │
│  (A) make fun of               (C) praise                    │
│  (B) assemble                  (D) drink                     │
├──────────────────────────────────────────────────────────────┤
│  [h] Hint (1/3)   [1‑4] Answer   [q] Quit                    │
└──────────────────────────────────────────────────────────────┘
```

*Hint sequence*

```text
Hint 1 (alt sentence): They always **mock** her accent behind her back.
Hint 2 (synonyms): ridicule · taunt · sneer
Hint 3 (translation): zombar (PT‑BR)
```

After Hint 3, pressing **h** flashes **“No more hints.”**

### 8.2 WordMCQ

```text
┌──────────────────────────────────────────────────────────────┐
│  With the exam tomorrow, you're ______ to feel nervous.      │
├──────────────────────────────────────────────────────────────┤
│  Definition: certain or inevitable to happen                 │
│                                                              │
│  (A) bound                     (C) doomed                    │
│  (B) tied                      (D) freed                     │
├──────────────────────────────────────────────────────────────┤
│  [h] Hint (1/3)   [1‑4] Answer   [q] Quit                    │
└──────────────────────────────────────────────────────────────┘
```

*Hint sequence*

```text
Hint 1 (synonym): certain
Hint 2 (second synonym): destined
Hint 3 (translation): certo (PT‑BR)
```

Further presses of **h** show **“No more hints available.”**

### 8.3 Typing

```text
┌──────────────────────────────────────────────────────────────┐
│  Her eyes were ______ with tears of joy.                     │
├──────────────────────────────────────────────────────────────┤
│  Definition: overflowing                                    │
│                                                              │
│  » bri…                                                      │
│  Your answer: ____________                                   │
├──────────────────────────────────────────────────────────────┤
│  [h] Hint (prefix/suffix)   [Enter] Submit   [q] Quit        │
└──────────────────────────────────────────────────────────────┘
```

*Hint sequence*

```text
Hint 1 (prefix): bri…
Hint 2 (suffix): …ming
```

Once both parts have appeared, extra presses flash **“No more hints.”**

### 8.4 Answer Feedback & Navigation

```text
✔ Correct!  Next due in 4 days.
— Definition: make fun of
Press [Enter] to continue.

✖ Wrong.  Correct answer: bound
Definition: certain or inevitable to happen
Press [Enter] to continue.
```

- The right/wrong banner always appears.
- The correct answer is **always** shown.
- No retry loop—press Enter to move to the next card.

