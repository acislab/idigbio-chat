import json
from io import StringIO

import dotenv
import numpy as np
import requests as rq
import pandas as pd
from openai import OpenAI

dotenv.load_dotenv()
client = OpenAI()


def get_embedding(text, model="text-embedding-3-small"):
    # text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def test_make_term_docs():
    response = rq.get("https://raw.githubusercontent.com/tdwg/dwc/refs/heads/master/vocabulary/term_versions.csv")
    terms = pd.read_csv(StringIO(response.text)).set_index("term_iri")
    terms = terms[terms["status"] != "superseded"] \
        [["iri", "term_localName", "label", "definition", "comments"]]
    terms.to_csv("dwc_terms.csv")


def test_dwc_terms_embed():
    response = rq.get("https://raw.githubusercontent.com/tdwg/dwc/refs/heads/master/vocabulary/term_versions.csv")
    terms = pd.read_csv(StringIO(response.text)).set_index("term_iri")
    terms = terms[terms["status"] != "superseded"] \
        [["iri", "term_localName", "label", "definition", "comments"]]

    def make_term_doc(term_data: pd.Series):
        return "\n".join([f"{k}: {v}" for k, v in term_data.to_dict().items()])

    docs = terms.apply(make_term_doc, axis=1)
    terms["embedding"] = docs.apply(lambda x: get_embedding(x))

    terms[["term_iri", "embedding"]].to_csv("dwc_term_embeddings.csv", index=False)


def test_dwc_terms_embed_minimal():
    response = rq.get("https://raw.githubusercontent.com/tdwg/dwc/refs/heads/master/vocabulary/term_versions.csv")
    terms = pd.read_csv(StringIO(response.text)).set_index("term_iri")
    terms = terms[terms["status"] != "superseded"]

    def make_term_doc(row):
        return "\"{label}\": {definition} {comments}".format(**row)

    docs = terms.apply(make_term_doc, axis=1)
    embeddings = docs.apply(lambda x: get_embedding(x)).rename("embedding")

    embeddings.to_csv("dwc_term_embeddings_label_definition_comments.csv")


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def rank_terms(df, query):
    embedding = get_embedding(query)
    df["similarities"] = df["embedding"].apply(lambda x: cosine_similarity(x, embedding))
    res = df.sort_values("similarities", ascending=False)
    return res


def test_vector_search():
    term_embeddings = pd.read_csv("dwc_term_embeddings_label_definition_comments.csv",
                                  converters={"embedding": json.loads})
    res = rank_terms(term_embeddings, "does the record describe just an observation or a real specimen?")
    pass
