"""
Stages 3 and 4 of the pipeline: embedding chunks and retrieving them.

Three things in here are worth knowing about, because they'd quietly break the
rest of the project if they were wrong:

1. The Chroma collection is created with cosine distance, explicitly. Chroma
   defaults to squared L2, and the 0.6 threshold the course uses is calibrated
   against cosine. Getting this wrong makes every distance number meaningless.

2. `search` returns the distance alongside each chunk. Milestone 4 has you
   compare distances, so they have to be visible.

3. The embedding model is the one Chroma bundles, not one loaded through
   `sentence-transformers`. It is the same model — `all-MiniLM-L6-v2`, 384
   dimensions — but it arrives as an ONNX build from Chroma's own CDN, so the
   install needs neither PyTorch nor a reachable Hugging Face. See `_embedder`.

4. `search` is hybrid: cosine similarity alone was ranking some genuinely
   relevant chunks too low (a strong lexical match on "ticket costs" landing
   outside top_k because it wasn't the closest *semantic* neighbor). A BM25
   keyword score is fused in alongside the vector ranking via reciprocal rank
   fusion. `Result.distance` always stays the chunk's real cosine distance
   though, never a fused score — the gate's threshold in config.py is
   calibrated against cosine distance specifically, so that number has to stay
   meaningful on its own. See `_bm25_index` and `_fuse`.
"""

import os
import re
import shutil
from dataclasses import dataclass

# Must be set BEFORE chromadb is imported. Without it, some Chroma versions
# print "Failed to send telemetry event ..." on every single call — which looks
# exactly like a real error, isn't one, and cost a previous cohort a lot of
# confused help-channel messages.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import chromadb  # noqa: E402
from rank_bm25 import BM25Okapi  

import config
from chunker import Chunk


@dataclass
class Result:
    """One retrieved chunk and how far it was from the question."""

    text: str
    source: str
    label: str
    distance: float   # LOWER IS BETTER. 0.3 is close, 0.9 is unrelated.
    produced_by: str


_model = None

# The model Chroma bundles. Anything else in config.EMBEDDING_MODEL means
# "fetch that one from Hugging Face instead" — see `_embedder`.
BUNDLED_MODEL = "all-MiniLM-L6-v2"


class _OnnxEmbedder:
    """
    Chroma's built-in embedder, wrapped to look like the other two.

    Chroma's embedding functions are called directly and hand back numpy
    arrays. The rest of this file wants `.encode(texts)`, so the adapter lives
    here rather than making every caller care which embedder it got.
    """

    def __init__(self):
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

        self._ef = ONNXMiniLM_L6_V2()

    def encode(self, texts, show_progress_bar: bool = False):
        return [vector.tolist() for vector in self._ef(list(texts))]


def _sentence_transformer(name: str):
    """
    The escape hatch: any model that isn't the bundled one.

    Unit 2's "try a second embedding model" stretch option comes through here,
    and so does anything you set `EMBEDDING_MODEL` to. This path *does* need
    `sentence-transformers` and a reachable Hugging Face, neither of which the
    default install has — which is the whole point of the default install.
    """
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            f"config.EMBEDDING_MODEL is set to {name!r}, which isn't the model "
            f"Chroma bundles ({BUNDLED_MODEL!r}), so it has to be downloaded "
            f"from Hugging Face.\n"
            f"Install the optional dependency first:\n"
            f"    pip install 'sentence-transformers>=3.4,<3.5'\n"
            f"Or set EMBEDDING_MODEL back to {BUNDLED_MODEL!r}."
        ) from exc

    return SentenceTransformer(name)


def _embedder():
    """
    Load the embedding model once and keep it.

    First call is slow — it downloads about 80 MB. That's why setup happens
    before class.
    """
    global _model

    if _model is not None:
        return _model

    # Used only by this repo's own smoke test, which runs where no model can be
    # downloaded at all. Never set this yourself.
    if os.getenv("AI201_FAKE_EMBEDDINGS") == "1":
        from _smoke_embedder import FakeEmbedder

        _model = FakeEmbedder()
    elif config.EMBEDDING_MODEL == BUNDLED_MODEL:
        _model = _OnnxEmbedder()
    else:
        _model = _sentence_transformer(config.EMBEDDING_MODEL)

    return _model


def embed(texts: list[str]) -> list[list[float]]:
    """Turn text into vectors. Runs on your machine, costs no API quota."""
    vectors = _embedder().encode(texts, show_progress_bar=False)
    # sentence-transformers and the smoke stand-in return something with a
    # .tolist(); _OnnxEmbedder has already done that conversion itself.
    return vectors.tolist() if hasattr(vectors, "tolist") else vectors


def _client():
    return chromadb.PersistentClient(
        path=str(config.CHROMA_DIR),
        settings=chromadb.config.Settings(anonymized_telemetry=False),
    )


_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _readable_source(source: str) -> str:
    """`guide_thornby_wells.md` -> `guide thornby wells`.

    BM25 only ever sees the words actually in a chunk's text, and most chunks
    below a document's first one never repeat that document's name (see
    chunker.py::split_documents — only the opening chunk carries the `#`
    heading). Folding the filename in as extra tokens lets a question that
    names a place ("Thornby Wells") pull in that place's own chunks over a
    near-identical paragraph belonging to a different one.
    """
    stem = re.sub(r"\.[^.]+$", "", source)
    return re.sub(r"[_\-]+", " ", stem)


# One BM25 index per collection, rebuilt only when the index itself changes.
_bm25_cache: dict[str, tuple[BM25Okapi, list[dict]]] = {}


def _bm25_index(name: str, collection) -> tuple[BM25Okapi, list[dict]]:
    """Build (or reuse) the BM25 index for a collection, alongside the chunk
    records in the same order the index expects them back in."""
    cached = _bm25_cache.get(name)
    if cached is not None:
        return cached

    raw = collection.get(include=["documents", "metadatas"])
    records = [
        {
            "text": text,
            "source": str(meta.get("source", "unknown")),
            "index": meta.get("index", 0),
            "produced_by": str(meta.get("produced_by", "unknown")),
        }
        for text, meta in zip(raw["documents"], raw["metadatas"])
    ]

    corpus_tokens = [
        _tokenize(r["text"] + " " + _readable_source(r["source"])) for r in records
    ]
    bm25 = BM25Okapi(corpus_tokens)

    _bm25_cache[name] = (bm25, records)
    return bm25, records


def _fuse(vector_order: list[str], bm25_order: list[str], k: int = 60) -> dict[str, float]:
    """Reciprocal rank fusion: combine two rankings (lists of ids, best first)
    into one score per id. A constant `k` keeps a #1-vs-#2 gap from swamping
    everything past it — standard RRF, no score normalization needed since it
    only ever looks at rank position, not the raw distance/BM25 scores."""
    scores: dict[str, float] = {}
    for order in (vector_order, bm25_order):
        for rank, item_id in enumerate(order):
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank + 1)
    return scores


def build_index(
    chunks: list[Chunk],
    corpus: str | None = None,
    variant: str = "default",
) -> int:
    """
    Embed every chunk and store it.

    `variant` lets you keep more than one index of the same corpus at the same
    time. In unit 2, when you compare two chunking strategies, index the second
    one as variant="v2" and you can query both instead of deleting the first
    and starting over.
    """
    name = config.collection_name(corpus, variant)
    client = _client()
    _bm25_cache.pop(name, None)

    try:
        client.delete_collection(name)
    except Exception:
        pass

    collection = client.create_collection(
        name=name,
        # ⚠️ Do not remove. Chroma defaults to squared L2, and every distance
        # number in this course assumes cosine.
        metadata={"hnsw:space": "cosine"},
    )

    batch = 256
    for start in range(0, len(chunks), batch):
        window = chunks[start : start + batch]
        collection.add(
            ids=[f"{c.source}#{c.index}" for c in window],
            documents=[c.text for c in window],
            embeddings=embed([c.text for c in window]),
            metadatas=[
                {"source": c.source, "index": c.index, "produced_by": c.produced_by}
                for c in window
            ],
        )

    return len(chunks)


def search(
    question: str,
    top_k: int | None = None,
    corpus: str | None = None,
    variant: str = "default",
) -> list[Result]:
    """
    Retrieve the chunks closest in meaning to a question.

    This is hybrid: a vector (cosine) ranking and a BM25 keyword ranking are
    each computed over the *whole* collection, then combined with reciprocal
    rank fusion (see `_fuse`). A chunk that's a strong lexical match but a
    middling semantic one — or vice versa — can still make the final top_k.

    Returns them by fused rank, each still carrying its real cosine distance
    (not a fused score) — the gate and the "best distance" reporting depend on
    that number meaning what it always meant.
    """
    top_k = top_k or config.TOP_K
    name = config.collection_name(corpus, variant)

    try:
        collection = _client().get_collection(name)
    except Exception as exc:
        raise RuntimeError(
            f"No index called '{name}'. Run `python app.py index` first."
        ) from exc

    total = collection.count()
    if total == 0:
        return []

    # Full cosine ranking, not just top_k, so a chunk that's a great lexical
    # match but a mediocre semantic one still has a real distance on record.
    raw = collection.query(query_embeddings=embed([question]), n_results=total)
    vector_order: list[str] = []
    distance_by_id: dict[str, float] = {}
    record_by_id: dict[str, dict] = {}
    for doc_id, text, meta, distance in zip(
        raw["ids"][0], raw["documents"][0], raw["metadatas"][0], raw["distances"][0]
    ):
        vector_order.append(doc_id)
        distance_by_id[doc_id] = float(distance)
        record_by_id[doc_id] = {
            "text": text,
            "source": str(meta.get("source", "unknown")),
            "index": meta.get("index", 0),
            "produced_by": str(meta.get("produced_by", "unknown")),
        }

    bm25, bm25_records = _bm25_index(name, collection)
    bm25_ids = [f"{r['source']}#{r['index']}" for r in bm25_records]
    bm25_scores = bm25.get_scores(_tokenize(question))
    bm25_order = [
        doc_id for doc_id, _ in sorted(
            zip(bm25_ids, bm25_scores), key=lambda pair: pair[1], reverse=True
        )
    ]

    fused = _fuse(vector_order, bm25_order)
    ranked_ids = sorted(fused, key=fused.get, reverse=True)[:top_k]

    # The single closest chunk by cosine is what the gate's threshold is
    # calibrated against (see gate.py). Fusion almost always keeps it near the
    # top anyway, but "almost always" isn't good enough for a number a
    # criterion depends on, so it's guaranteed a seat.
    best_vector_id = vector_order[0]
    if best_vector_id not in ranked_ids:
        ranked_ids[-1] = best_vector_id

    results: list[Result] = []
    for doc_id in ranked_ids:
        record = record_by_id.get(doc_id) or next(
            r for r in bm25_records if f"{r['source']}#{r['index']}" == doc_id
        )
        results.append(
            Result(
                text=record["text"],
                source=record["source"],
                label=doc_id,
                distance=distance_by_id[doc_id],
                produced_by=record["produced_by"],
            )
        )
    return results


def index_exists(corpus: str | None = None, variant: str = "default") -> bool:
    """Is there an index here to search, without searching it?

    `serve.py`'s health check asks this. It deliberately does not embed
    anything: loading the embedding model takes 80 MB and a few seconds, and a
    health check that heavy is a health check nobody can afford to call.
    """
    try:
        collection = _client().get_collection(config.collection_name(corpus, variant))
        return collection.count() > 0
    except Exception:
        return False


def reset():
    """Delete every index. Occasionally the fastest way out of a mess."""
    if config.CHROMA_DIR.exists():
        shutil.rmtree(config.CHROMA_DIR)
