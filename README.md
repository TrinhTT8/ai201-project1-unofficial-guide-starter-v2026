# The Unofficial Guide

**Trinh Tran**

**Chosen corpus**: city_guides

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

This repo uses the city_guides corpus, regional travel guides covering practical details across several villages and towns, like transit costs, market days, accessibility, and seasonal opening times. The system answers specific questions a traveler would actually ask before a trip (e.g. "How available is cash in Thornby Wells?" or "What's a tip for saving on ticket costs in Marchwood?"), retrieving the guide passages that support each answer and naming the source document. The system will also refuse questions that are outside of the scope and not covered within the guide.

## Chunking Strategy

**Chunk size**: Not needed

**Overlap**: Not needed

<!-- What about YOUR documents made you pick these numbers? Short posts and
     long sectioned guides don't want the same chunking, and "800 seemed
     reasonable" earns nothing. Point at something you noticed when you read
     the documents in Milestone 1.

     If you changed your mind partway through, say so and say why. That's worth
     more than pretending you got it right first time.

     Milestone 3. -->

City_guides documents contain mostly paragraphs, separated by headlines and blank spaces. In the beginning, I was setting up the chunk size to be around 200 and an overlap of 10
because I was counting the average characters in each paragraph, and most of them are around 150-250 characters. However, after doing more research, I realized that it makes
more sense to divide the chunks into paragraphs. This way, the context is not being cut, and we keep all the related information grouped.

I didn't use chunk size or overlap here because my function already determined a concrete boundary for each paragraph. Instead of relying on the number of characters, I just
search for white spaces. This tradeoff preserves paragraphs, but it also does not enforce a maximum chunk length.

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `guide_accessibility.md#0` — produced by: `chunker.py::split_documents`

```
# Getting around the region with limited mobility

An honest assessment rather than a promotional one. Some of these places are
difficult and it is better to know in advance.
```

**Chunk 2** — source: `guide_corry_vale.md#4` — produced by: `chunker.py::split_documents`

```
## What to see

The valley itself is the attraction. The footpath network is dense and well marked, and a circuit taking in three of the four villages is about nine miles with 500 metres of ascent. The chapel in the second village is 12th century and always unlocked.
```

**Chunk 3** — source: `guide_givens_mill.md#4`— produced by:`chunker.py::split_documents`

```
## What to see

The mill runs tours on the hour from 11 to 3 and the machinery is operating during them, which is loud and much more impressive than a static exhibit. The church has a Saxon doorway. The river walk downstream reaches Brightwater in about three hours.
```

**Chunk 4** — source: `guide_marchwood.md#3`— produced by:`chunker.py::split_documents`

```
The best eating is in the Northgate district, a 12-minute tram ride from the station, where about thirty restaurants sit within four streets. The area immediately around the station is uniformly poor and expensive. Marchwood keeps later hours than anywhere else in the region — kitchens serve until 10:30pm, and until midnight onFridays and Saturdays.``
```

**Chunk 5** — source: `guide_seasons.md#2`— produced by:`chunker.py::split_documents`

```
## Summer, June to August

June is excellent everywhere. July and August split: Halden Bay becomes very
busy and the parking problem dominates, Kestrelford fills with walkers, and
Brightwater goes quiet to the point of dullness with the university empty.
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question**: What is a good market for Saturday and weekday morning within the region?

**Answer**: For a Saturday market, Kestrelford's market has run since the 1400s and is the region's best (`guide_eating.md` and `guide_kestrelford.md`). For a weekday morning, Marchwood's covered market is at its best at that time (`guide_eating.md`).

```
Sources retrieved: guide_brightwater.md, guide_eating.md, guide_kestrelford.md
```

**My relevance cutoff**: 0.7

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

| Question     | In corpus? | Best distance |
| ------------ | ---------- | ------------- |
| Covered Q1   | Yes        | 0.411         |
| Covered Q2   | Yes        | 0.5533        |
| Covered Q3   | Yes        | 0.5630        |
| Covered Q4   | Yes        | 0.5255        |
| Covered Q5   | Yes        | 0.3389        |
| Uncovered Q1 | No         | 0.803         |
| Uncovered Q2 | No         | 0.892         |
| Uncovered Q3 | No         | 0.975         |
| Uncovered Q4 | No         | 0.837         |
| Uncovered Q5 | No         | 0.813         |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.** I used AI to walk me through the code within the given functions. I came up with the logic of the chunking function, explained it to Claude and asked it to generate the function for me. I took out the chunk size and overlap since I deemed them as unecessary.

**2.** After running all of the 5 covered and 5 uncovered questions, I pasted the best distances to Claude and explained why I chose 0.7 as my cutoff number. Combining wih the guided questions in Milestone 4, I had Claude reply with the most appropriate cutoff number and why. It also suggested somewhere between 0.5 and 0.7.

**3.** For Unit 2, I used AI to help me with adding in keyword search code. I explained to Claude what I wanted to achieve by adding BM25 alongside matching on meaning. I had it generate the new function for me as I cross-checked the logic of the code. 

**4.** I also leveraged Claude in diagnosing the miss. Initially, I thought the miss happened in the chunking stage; however, with Claude guiding me through the runs and doing a little bit more diagnosis, it suggested that the issue was within the retrieval and embedding stages instead. 

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion                                   | Target | Run 1 | Run 2 | Run 3 | Verdict |
| ------------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer      | 4 of 5 | 3/5   | 3/5   | 3/5   | MISSED  |
| 2. Every answer names a source              | 5 of 5 | 3/5   | 3/5   | 3/5   | MISSED  |
| 3. Gate stops out-of-corpus questions       | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 4. Chunk length (200 - 700 characters)      | 4 of 5 | 3/5   | 3/5   | 3/5   | MISSED  |
| 5. Contained complete sentence or paragraph | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

### 1. Retrieved chunks contain the answer

Produced by: `store.py::search`, chunks from `chunker.py::split_documents`

**During what season shouldn't you visit Given Mills?**, top chunk, `guide_givens_mill.md`:
"The mill runs March to November and is closed entirely in winter."
→ contains the answer.

**How available is cash for Thornby Wells and Pellew Sands?**, top chunk, `guide_eating.md`:
"Cash is still useful at markets and in the smaller villages. Corry Vale has a
farm shop..." (about Corry Vale/Elder Ness, not Thornby Wells/Pellew Sands)
→ does not contain the answer.

### 2. Every answer names a source

Produced by: `generate.py::answer_from_chunks`, run_2026-09-23_1952_before.md, run 1

**What is a good market for Saturday and weekday morning within the region?**
"Kestrelford's Saturday market runs year-round (though much reduced from
November to February), and Marchwood's covered market is at its best on a
weekday morning.

Source: `guide_eating.md`"

**How available is cash for Thornby Wells and Pellew Sands?**
"I do not have enough information to answer how available cash is for
Thornby Wells and Pellew Sands."

→ no source named (this is the refusal case worth noting in your write-up).

### 3. The relevance gate stops out-of-corpus questions

Produced by: `run_eval.py::check_out_of_scope`

| Out-of-scope question                                       | Best distance | Gate    |
| ----------------------------------------------------------- | ------------- | ------- |
| What is the capital of Mongolia?                            | 0.803         | refused |
| How do I change the oil in a diesel engine?                 | 0.892         | refused |
| Who won the 1994 World Cup?                                 | 0.975         | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.849         | refused |
| How do I write a for loop in Rust?                          | 0.813         | refused |

Refused 5 of 5.

### 4. Chunk length (200-700 characters)

Produced by: `store.py::search`

"What does the guide say about parking?", top chunk, `guide_regional_transport.md`, 167 chars:
"Parking is the constraint rather than driving. Both Halden Bay lots fill by
10am on summer weekends. Kestrelford's lower car park is free and involves a
steep walk up."
→ out of range (too short).

### 5. Chunks contain a complete sentence or paragraph

Produced by: `store.py::search`

"What is a good market for Saturday and weekday morning within the region?", top chunk, `guide_eating.md`:
"## Markets

Kestrelford's Saturday market has run since the 1400s and is the region's best,
though much reduced from November to February..."
→ complete heading + full sentences, no mid-cut.

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| #   | Criterion                                   | Verdict | How I decided                                                                                                                                                                                                                         |
| --- | ------------------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Retrieved chunk contains the answer         | MISSED  | Only 3 of 5 top chunks actually contained the answer. The ticket-cost chunk never mentions day tickets or single fares, and the cash-availability chunk names different villages (Corry Vale, Elder Ness) than the ones asked about. |
| 2   | Every answer names a source                 | MISSED  | 3 of 5 answers named a source; the two refused answers (cash, ticket costs) named none, since the model had nothing grounded to cite.                                                                                                 |
| 3   | Gate stops out-of-corpus questions          | MET     | The gate refused all 5 out-of-corpus questions (best distance 0.803 or higher), clearing the 4-of-5 target with no borderline cases.                                                                                                  |
| 4   | Chunk length (200 - 700 characters)         | MISSED  | Only 3 of the 5 top-retrieved chunks fell in the 200-700 character range (60%), well short of the 90% target.                                                                                                                         |
| 5   | Chunk contain a complete sentence/paragraph | MET     | All 5 top-retrieved chunks ended on a complete sentence or heading, with no mid-thought cuts.                                                                                                                                         |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

**Criterion 1** (retrieved chunk contains the answer): Stage is retrieval/embedding, not chunking. Two questions failed here. For "What is a tip to saving ticket costs in Marchwood that nobody tells you?", the answer is literally sitting in the corpus: guide_marchwood.md has a chunk that says "A day ticket costs less than two single fares and nobody tells you this at the machine," basically a direct match. When I searched past my usual top_k=4 to see where that chunk actually ranked, it came back at position 12 out of 15. So it's not that chunking cut the sentence apart or that the fact is missing from my corpus, retrieval just did not rank it high enough to make the cut. For "How available is cash for Thornby Wells and Pellew Sands?", the mechanism is different but still retrieval. Almost every village guide in my corpus has a near-identical "Practical notes" paragraph that starts "Cash is still useful at the market and in smaller places..." It is basically boilerplate repeated across most documents. Because the wording is so similar everywhere, the embeddings can't tell which village's copy is the relevant one, so Thornby Wells' own version did not even show up in my top 15 results. What got retrieved instead were the intro chunks for those two villages, which name the towns but say nothing about cash.

**Criterion 2** (every answer names a source): Same stage, retrieval/embedding, and the same two questions. This isn't a separate failure, it's a downstream effect of criterion 1. Since the chunk with the actual answer never made it into the top_k=4 for either question, the model never saw it, and per its grounding instruction it correctly said it did not have enough information instead of naming a source it never received. So the mechanism is: retrieval failure upstream means generation has nothing to cite.

**Criterion 4** (90% of chunks between 200 and 700 characters): Stage is chunking. My chunker splits purely on paragraph breaks with no minimum length, so short paragraphs, like a one-line heading or a short intro sentence, become their own tiny chunk. Every chunk that fell outside my 200 to 700 range was too short (the longest "too short" one was 199 characters, and nothing was ever too long), which matches that mechanism: the splitter has no lower bound, so it produces very short chunks whenever a paragraph in the source document is short.

## The Improvement

**What I changed:** I made retrieval hybrid in store.py::search. Before, it only ranked chunks by cosine distance from the embeddings. Now it also runs a BM25 keyword search over the same chunks and combines both rankings with reciprocal rank fusion before picking the top_k. I also fed each chunk's source filename into the BM25 index (not just the chunk text itself), since most chunks past a document's first one never repeat that document's place name. The gate still uses the real cosine distance, not a fused score, so I didn't touch how the threshold works.

**Why I picked it:** This connects straight to my criterion 1 diagnosis. The ticket-cost question failed not because the answer was missing from my corpus or got cut apart by chunking, it was sitting in guide_marchwood.md as a full paragraph, it just ranked 12th out of 15 by pure cosine distance and never made it into my top 4. That's a retrieval/embedding-stage problem, so I picked a retrieval-stage fix instead of touching my chunker again.

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion                                    | Target | Run 1 | Run 2 | Run 3 | Verdict |
| --------------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer        | 4 of 5 | 4/5   | 4/5   | 4/5   | MET     |
| 2. Every answer names a source                | 5 of 5 | 4/5   | 4/5   | 4/5   | MISSED  |
| 3. Gate stops out-of-corpus questions         | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 4. Chunk length (200 - 700 characters)        | 4 of 5 | 3/5   | 3/5   | 3/5   | MISSED  |
| 5. Contained complete sentence or paragraph   | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |

**Did it help?**

Yes, but only on the one question it targeted. Criterion 1 went from MISSED (3/5) to MET (4/5): the ticket-cost question now passes all 3 runs, every time correctly citing `guide_marchwood.md`'s day-ticket line, the exact chunk that used to rank 12th of 15 and miss the top 4. Criterion 2 improved for the same reason (3/5 to 4/5) but is still MISSED against its 5-of-5 target, since the cash-availability question is unchanged. Criterion 4 stayed MISSED at 3/5, just with a different question now falling short, a side effect of ranking by fused score instead of pure cosine distance.

One honest observation: I ran the after-eval three separate times, and the cash question's retrieval wasn't consistent between them, two runs refused every time, one got lucky and pulled in the right village-specific chunk. Likely cause is Chroma's approximate nearest-neighbor search being sensitive to several near-identical "Practical notes" paragraphs across villages sitting very close together in embedding space. I used the more typical (2-of-3) outcome for the numbers above rather than the lucky run.

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

**Criterion 2** (every answer names a source, 4/5, target 5/5): the cash-availability question is the one holding this back. Thornby Wells and Pellew Sands both have their own "Practical notes" paragraph with the actual cash info, but it's nearly word-for-word identical to seven other villages' versions, so nothing in retrieval, keyword or vector, can reliably tell them apart. What I'd try next is folding each village's name into its own chunks before embedding (not just the filename into the BM25 index like I did this round), so "Thornby Wells: cash is still useful..." embeds differently from the same sentence under a different village. I stopped short of doing this because I'd already spent my one Unit 2 fix on the retrieval-ranking problem, and this turned out to need a chunking-stage change instead, which is a second, separate fix I didn't have time to also implement and re-evaluate.

**Criterion 4** (chunk length 200-700 characters, 3/5): still short chunks, same root cause as before the fix, my chunker has no minimum paragraph length, so a one-line heading or short intro becomes its own tiny chunk. The fix is straightforward, merge any chunk under some minimum (say 150 characters) into its neighbor, but I didn't touch it because my Unit 2 diagnosis pointed at retrieval, not chunking, and I wanted my one change to match my one diagnosis rather than bundling two fixes together and losing track of which one did what.

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->

**Criterion 4** is the one I'd rewrite. Criteria.md says "at least 90% of chunks," but the Run Log tables score it against 5 sampled questions, and 90% of 5 isn't a whole number, so in practice I've been treating it as "4 of 5" without ever writing that down as the actual target. That's the same kind of problem the course warns about with criterion 1 in the worked example, a target that can't be checked the same way twice. I'd rewrite it against a fixed, larger sample (all chunks in the corpus, which I already have code to compute) instead of 5 questions' worth of top-ranked chunks, so the percentage means what it says.

**Criterion 2** is the other one. Right now it silently counts a correct refusal (the gate/model correctly saying "not enough information") the same as an answer that should have had a source but didn't. Those are different failures, one is retrieval not finding the right chunk, the other would be the model citing nothing for an answer it did generate. I'd split it into two criteria next time so a diagnosis doesn't have to untangle which one actually happened after the fact.
