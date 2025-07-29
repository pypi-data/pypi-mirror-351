import sys
import os
import time
import math
from contextlib import contextmanager
from datetime import date
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

project_root = os.path.abspath(os.path.join(os.getcwd(), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sentence_transformers import SentenceTransformer
from app.db.elastic_auth import ElasticSearch
from app.shared_config import SearchConfig


config: SearchConfig = SearchConfig()
model: SentenceTransformer = config.model
INDEX: str = config.index
VECTOR_FIELD: str = config.vector_field

es: ElasticSearch = ElasticSearch()

@contextmanager
def timed(label: str = "elapsed") -> Iterable[None]:
    """
    Context manager to measure wall-clock time in milliseconds.
    Usage:
        with timed("k-NN query"):
            hits = search_knn(vec)
    """
    start = time.perf_counter()
    yield
    elapsed_ms = (time.perf_counter() - start) * 1_000
    print(f"{label}: {elapsed_ms:.2f} ms")


def evaluate_results(hits: Dict[str, Any], relevant_ids: Sequence[str], k: int = 10) -> Tuple[float, float]:
    """
    Compute precision@k and nDCG@k given a raw ES response.
    - hits:      output of search_script_score or search_knn
    - relevant_ids: ground-truth list of doc IDs (strings)
    - k:         cutoff rank
    Returns: (precision@k, nDCG@k)
    """
    retrieved: List[str] = [
        h["_id"] for h in hits.get("hits", {}).get("hits", [])[:k]
    ]

    # Precision@k
    num_rel = sum(1 for doc_id in retrieved if doc_id in relevant_ids)
    precision_k = num_rel / float(k)

    # DCG
    dcg = 0.0
    for i, doc_id in enumerate(retrieved, start=1):
        if doc_id in relevant_ids:
            dcg += 1.0 / math.log2(i + 1)

    # IDCG
    ideal_rels = min(len(relevant_ids), k)
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, ideal_rels + 1))

    ndcg_k = dcg / idcg if idcg > 0 else 0.0
    return precision_k, ndcg_k


def search_script_score(vec: Sequence[float],lang: str = "en",k: int = 10) -> Dict[str, Any]:
    """
    Cosine-based script_score query.

    Parameters
    ----------
    vec : query embedding as list of floats
    lang: two-letter language code to filter
    k   : number of hits

    Returns
    -------
    Raw Elasticsearch JSON response.
    """
    body: Dict[str, Any] = {
        "size": k,
        "_source": ["id", "post", "lang", "location"],
        "query": {
            "script_score": {
                "query": {
                    "bool": {"must": [{"term": {"lang": lang}}]}
                },
                "script": {
                    "source": "cosineSimilarity(params.query_vector, doc['VECTOR_FIELD']) + 1.0",
                    "params": {"query_vector": vec}
                }
            }
        }
    }
    return es.search_documents(index=INDEX, **body)


# def search_knn(vec: Sequence[float],lang: Optional[str] = None, k: int = 10) -> Dict[str, Any]:
#     """
#     Native k-NN (approximate) dense-vector query.

#     Parameters
#     ----------
#     vec : query embedding
#     lang: optional language filter
#     k   : number of hits

#     Returns
#     -------
#     Raw Elasticsearch JSON response.
#     """
#     body: Dict[str, Any] = {
#         "size": k,
#         "_source": ["id", "post", "lang", "location"],
#         "knn": {
#             "field": VECTOR_FIELD,
#             "k": k,
#             "num_candidates": 100,
#             "query_vector": vec
#         }
#     }
#     if lang:
#         body["knn"]["filter"] = {"bool": {"must": [{"term": {"lang": lang}}]}}
#     return es.search_documents(index=INDEX, **body)


# if __name__ == "__main__":
#     # query = "Je viens de commander du poulet frit"
#     query="non alcoholic"
#     vec = model.encode(query).tolist()

#     # measure knn
#     with timed("k-NN search"):
#         knn_hits = search_knn(vec, lang="en")

#     # if you have ground-truth IDs, you can now evaluate:
#     # relevant = ["5525401494972942513", "6350111674118398826", "8514894905895725575"] 
#     # p_knn, ndcg_knn = evaluate_results(knn_hits, relevant, k=2)
#     # print(f"k-NN  → precision@10={p_knn:.2%}, nDCG@10={ndcg_knn:.3f}")

#     print("\n--- KNN RESULTS ---")
#     for h in knn_hits.get("hits", {}).get("hits", []):
#         print(f"{h['_source']['lang']} – {h['_source']['post']}")


def search_knn(vec: Sequence[float], lang: str = None, k: int = 10) -> Dict[str, Any]:
    """
    k-NN search on `post_embed` using a pre-computed embedding.

    Parameters
    ----------
    vec  : 384-D query vector (list / tuple / ndarray of floats)
    lang : two-letter language code; None ⇒ no language filter
    k    : number of results to return

    Returns
    -------
    Raw Elasticsearch response (dict)
    """
    # fixed window you asked to keep inside the payload
    date_from = "2022-01-01"
    date_to   = date.today().isoformat()
    num_candidates = 50          # ef_search shortlist

    must_clauses = [
        {"range": {"created_timestamp": {"gte": date_from, "lte": date_to}}}
    ]
    if lang:
        must_clauses.append({"term": {"lang": lang}})

    body: Dict[str, Any] = {
        "size": k,
        "_source": False,
        "fields": ["id", "post", "lang", "location", "created_timestamp"],
        "knn": {
            "field": "post_embed",
            "k": k,
            "num_candidates": num_candidates,
            "query_vector": vec,
            "filter": {"bool": {"must": must_clauses}},
        },
    }

    return es.search_documents(index=INDEX, **body)



# ── quick demo ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    query = "non alcoholic"
    vec = model.encode(query).tolist()          # local embedding

    # language-agnostic search
    hits = search_knn(vec, lang="en", k=10)

    # language-specific search
    # hits = search_knn(vec, lang="en", k=10)

    for h in hits.get("hits", {}).get("hits", []):
        f = h["fields"]                 # note: each value is a list
        print(f"{f.get('lang', ['?'])[0]} — {f['post'][0][:100]}…")


