# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:** One of my questions — "During what season shouldn't you visit
Given Mills?" — is answered by a single sentence in one document
(`guide_givens_mill.md`), with no mention of it in `guide_seasons.md` or
anywhere else. If retrieval pulls in a chunk about a different village's
seasonal advice instead, that one question could miss, so I'm not requiring
5 of 5.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target**: Most of my questions specify the specific region/source so the answer should be referenced from that particular source easily.
<!-- Why all five and not four? What about your setup makes that achievable —
     or what would have to go wrong for it not to be? -->

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:** My five covered questions had best distances between
0.339 and 0.563, and my five out-of-scope questions had best distances
between 0.803 and 0.975 — a clean gap with no overlap. I set the cutoff at
0.7, roughly the midpoint of that gap, so it doesn't hug either group's edge.
I'm not requiring 5 of 5 because this gap came from only five examples on
each side; a question worded less like the source text could plausibly land
closer to the boundary than anything I tested.

---

## 4. Something about your chunks
At least 90% of chunks are longer than 200 characters and shorter than 700 characters, so each result focuses on an appropriate amount of information.



**Why this target**: My chunker splits on paragraph boundaries rather than a fixed size, so I don't directly control chunk length. This criterion checks whether that choice produces reasonably-sized chunks as a side effect. When I read the documents in Milestone 1, most paragraphs ran 150–250 characters, so I expect the resulting chunks to mostly land in the 200–700 range. I'm not requiring 100% because a paragraph splitter will occasionally produce a short one-line heading or a long uninterrupted paragraph, and I'd rather have that show up as a measurable miss than pretend my boundary logic is 100% accurate.


---

## 5. Your choice
At least 4 of 5 sampled chunks contain a complete sentence or paragraph.

**Why this target**: A chunk that ends in the middle of a sentence or paragraph may leave out important context and make the retrieved answer harder to understand. I chose 4 out of 5 because checking a sample gives me a practical way to measure whether the chunking strategy usually preserves complete ideas.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
