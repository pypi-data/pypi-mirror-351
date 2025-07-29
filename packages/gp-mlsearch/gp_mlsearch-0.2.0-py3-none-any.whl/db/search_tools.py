import pandas as pd
from app.db.elastic_auth import ElasticSearch
from typing import List, Dict, Optional,Annotated
from annotated_types import Len

from sentence_transformers import SentenceTransformer
from pydantic import BaseModel, Field, conlist
from pydantic.functional_validators import model_validator # type:ignore

from app.shared_config import SearchConfig

config = SearchConfig()

MODEL = config.model
INDEX = config.index
VECTOR_FIELD = config.vector_field
# VECTOR_LENGTH = len(MODEL.encode("hello world"))
es = ElasticSearch()

# class SearchParams(BaseModel):
#     query_term: Optional[str] = ""
#     vector: Optional[Annotated[list, Len(min_length=VECTOR_LENGTH, max_length=VECTOR_LENGTH)]] = None

#     @model_validator(mode='after')
#     def check_one_of(self):
#         query_term = self.query_term
#         vector = self.vector
#         if query_term and vector:
#             raise ValueError("You must provide either a query term or a vector, not both.")
#         if not query_term and not vector:
#             raise ValueError("You must provide at least one of query_term or vector.")

#         return self



def ts_query(term: str, threshold: float, country: str | None = None) -> dict | list[dict]:
    
    term_vector = MODEL.encode(term).tolist()

    
    q = {
        "size":0,
        # "_source":False, 
        # "fields": ["id","post","lang","location"],
        "query": {
            "script_score": {
                "query": {
                    # "match_all":{}
                    # "bool": {
                    #     "must": [ {"match": {"location": country}} ]
                    # }
                },
                "script": {
                    "source": "cosineSimilarity(params.query_vector, doc[VECTOR_FIELD]) + 1",
                    "params": { "query_vector": term_vector }
                }
            }
        },
        "min_score": 1 + threshold,
        "aggs": {
            "posts_per_day": {
                "date_histogram": {
                    "field": "created_timestamp",
                    "calendar_interval": "week"
                }
            },
            "lang_buckets": {
                "terms": {
                    "field": "lang"
                }
            }
        }
    }
    
    q["query"]["script_score"]["query"] = { "bool": {"must": [ {"match": {"location": country}}] }} if country else {"match_all": {}}
    # find & filter & agg by day/week
    return es.search_documents(index=INDEX, **q)

def get_saturation(term: str, threshold: float, country: str| None= None) -> pd.DataFrame:
    """
    returned df will be a range of vals between 0 and 100
    """
    
    
    total_docs_ct = ts_query(term=term, threshold=0, country=country)['aggregations']['posts_per_day']['buckets']
    matching_docs_ct = ts_query(term=term,threshold=threshold, country=country)['aggregations']['posts_per_day']['buckets']
    #     timeseries = [
    #     (bucket["key_as_string"], bucket["doc_count"])
    #     for bucket in response["aggregations"]["posts_per_day"]["buckets"]
    # ]
    
    total_docs_df = pd.DataFrame(total_docs_ct)[['key_as_string', 'doc_count']].rename(columns={'key_as_string': 'date', 'doc_count': 'total_docs'})
    matching_docs_df = pd.DataFrame(matching_docs_ct)[['key_as_string', 'doc_count']].rename(columns={'key_as_string': 'date', 'doc_count': 'matching_docs'})
    
    print(total_docs_df)
    print(matching_docs_df)

    # Merge the two DataFrames on the 'date' column
    merged_df = total_docs_df.merge(matching_docs_df, on="date", how='outer').fillna(0)

    
    merged_df['sat'] = merged_df['matching_docs'] / merged_df['total_docs'] * 100
    merged_df['sat'].fillna(0, inplace=True) 

    # Calculate normalized saturation
    return merged_df
    
    
    

def search_snippets_with_lang(term: str, lang: str, location: str, k: int) -> list[dict]:
    # find & filter by both vector search and input language
    
    
    term_vector = MODEL.encode(term).tolist()
    
    q = {
        "size": 100,
        "_source": False, 
        "fields": ["id","post","lang","location","created_timestamp"],
        "knn": {
            "k": k,
            "field": VECTOR_FIELD,
            "query_vector": term_vector,
            "num_candidates": 10000,
            "filter": {
            "bool": {
                "must": [
                    { "term": { "lang": lang } },
                    # { "term": { "location": location } },
                    { "range": { "created_timestamp": { "gte": "2022-01-01", "lte": "2024-12-31" } } }
                ]
            }
            }
        }
    }
    
    return es.search_documents(index=INDEX, **q)






if __name__ == "__main__":
    
    
    # print(ts_query("oat milk",0.5))
    print("\n\n\n",get_saturation("oat milk",0.5))
    # print(
    #     ts_query("oat milk",0.4)
    # )
    
    # print(
    #     ts_query("oat milk",0.4,"BR")
    # )    
    # print(search_snippets_with_lang("oat milk", "es",50))
    # for i in search_snippets_with_lang("I am a gummy bear","en",'US',500)["hits"]["hits"]:
    #     doc = i["fields"]
    #     print(f"score={i['_score']:.3f} ISO2={doc['location'][0]}, lang_pred={doc['lang'][0]} {doc['post'][0]}")